from typing import Optional
import grpc
import uuid
from collections import defaultdict
from loguru import logger
from faststream.kafka import KafkaBroker

from src.repositories.message import MessageRepository
from src.services.user import UserService
from src.services.chat import ChatService
from src.models import Message, MetaData, ReplyData
from src.exceptions.message import *
from src.exceptions.chat import *
from src.exceptions.user import *
from src.schemas.message import *
from src.routers.kafka.producer import KafkaPublisher


class MessageService:
    def __init__(
            self, 
            repo: MessageRepository,
            user_service: UserService,
            chat_service: ChatService,
            kafka_producer: KafkaPublisher,
        ):
        self.repo = repo
        self.user_service = user_service
        self.chat_service = chat_service
        self.kafka_producer = kafka_producer

    async def get(self, message_id: str, get_full: bool = False) -> Message:
        logger.info(f"Получаем сообщение {message_id}")
        message = await self.repo.get(message_id, get_full=get_full)
        if not message:
            logger.warning(f"Не найдено сообщение {message_id}")
            raise MessageNotFoundError(message_id=message_id)
        return message

    async def get_all(self, chat_id: int):
        result = await self.repo.get_all(chat_id, fetch_links=True)
        logger.info(f"Получено {len(result)} сообщений из чата {chat_id=}")

        user_ids = list(set(message.user_id for message in result))
        users = await self.user_service.get_multiple(user_ids)
        user_dict = {}
        for user in users:
            user_dict[user.user_id] = user.username

        return result, user_dict
    
    async def insert(
            self, 
            user_id: int, 
            chat_id: int, 
            content: str, 
            request_id: str, 
            sender_id: int,
            reply_to: Optional[str] = None,
        ):
        errors = []
        try:
            chat = await self.chat_service.get(chat_id)
        except ChatNotFoundError:
            errors.append('chat_id')
        try:
            user = await self.user_service.get(user_id)
        except UserNotFoundError:
            errors.append('user_id')
        if not user.user_id in chat.members:           
            errors.append('user not is chat member')

        if errors:
            err_str = ', '.join(errors)
            logger.warning(f"Неверные данные: {err_str}")
            raise DataLossError(err_str)

        metadata = MetaData()
        if reply_to:
            reply_to_message = await self.get(reply_to)
            if reply_to_message.chat_id == chat_id:
                reply_to_user = await self.user_service.get(reply_to_message.user_id)
                reply_data = ReplyData(
                    message_id=reply_to,
                    user_id=reply_to_user.user_id,
                    username=reply_to_user.username,
                    preview=(reply_to_message.content 
                            if len(reply_to_message.content) <= 50 
                            else reply_to_message.content[:47]+"..."
                    )
                )
                metadata.reply_to = reply_data

        message = Message(
            user_id=user_id, 
            chat_id=chat_id, 
            content=content,
            metadata=metadata
        )
        message = await self.repo.insert(message)
        logger.info(f"Добавлено сообщение {message.id=} в {chat_id=}")

        users = await self.user_service.get_multiple(chat.members)
        active_recievers = [
            member.user_id for member in users 
            if member.is_active == True
        ]

        event_data = MessageData(
            id=str(message.id),
            chat_id= message.chat_id,
            content=message.content,
            sender=UserData(
                id=user.user_id,
                username=user.username
            ),
            created_at=message.created_at
        )
        await self.kafka_producer.create_message(
            recievers=active_recievers,
            data=event_data,
            request_id=request_id,
            sender_id=sender_id,
        )

        return message
    
    async def update(
        self, 
        message_id: str, 
        new_content: str, 
        request_id: str, 
        sender_id: int
    ) -> Message:
        logger.info(f"Обновляем сообщение {message_id}")

        message = await self.get(message_id)
        message = await self.repo.update(message, new_content)
        logger.info(f"Обновлено сообщение: {message_id}")

        active_recievers = await self.chat_service.get_active_members(chat_id=message.chat_id)
        event_data = UpdateMessagePayload(id=str(message.id), content=message.content)
        await self.kafka_producer.update_message(
            recievers=active_recievers,
            data=event_data,
            request_id=request_id,
            sender_id=sender_id,
        )
        logger.info(f"Уведомление об обновлении сообщения {message.id} отправлено")
        return message
    
    async def delete(
        self,
        message_id: str,
        request_id: str,
        sender_id: int
    ):
        logger.info(f"Удаляем сообщение {message_id}")
        message = await self.get(message_id)
        await self.repo.delete(message)
        logger.info(f"Удалено сообщение {message_id}")

        recievers = await self.chat_service.get_active_members(message.chat_id)
        await self.kafka_producer.delete_message(
            recievers=recievers,
            data=MessageIdPayload(id=str(message_id)),
            request_id=request_id,
            sender_id=sender_id,
        )
    
    async def delete_chat_messages(self, chat_id: int):
        logger.info(f"Удаляем сообщения чата {chat_id}")
        deleted_count = await self.repo.delete_chat_messages(chat_id)
        logger.info(f"Удалены {deleted_count} сообщения чата: {chat_id=}")


    async def mark_as_read(
            self, 
            chat_id: int, 
            user_id: int, 
            message_id: str
        ):
        logger.info(f"Обновляем последнее прочитанное сообщение")

        previous_read_message = await self.repo.get_last_read_message(chat_id=chat_id, user_id=user_id)
        await self.repo.set_last_read_message(chat_id, user_id, message_id)
        logger.info(f"Обновили счетчик последнего прочитанного сообщения")

        changed_messages = await self.repo.mark_as_read(
            previous_message_read=previous_read_message,
            last_read_message=message_id,
            read_by=user_id
        )
        if changed_messages:
            event_data = [SlimMessageData(id=str(message.id), sender_id=message.user_id) for message in changed_messages]
            await self.kafka_producer.read_message(data=event_data)

        logger.info(f"Последнее прочитанное сообщение пользователя {user_id} обновлено")

    async def add_reaction(
            self, 
            message_id: str, 
            reaction: str, 
            author: int
        ):
        await self.user_service.get(author)
        logger.info(f"Добавляем реакцию в сообщение: {message_id}")
        result = await self.repo.add_reaction(message_id, reaction, author)
        if result > 0:
            event_data = Reaction(
                message_id=message_id,
                author=author,
                reaction=reaction
            )
            await self.kafka_producer.add_reaction(event_data)
        else:
            raise ReacionNotAdded()

    async def remove_reaction(
            self, 
            message_id: str, 
            reaction: str, 
            author: int
        ):
        await self.user_service.get(author)
        logger.info(f"Удаляем реакцию реакцию из сообщения: {message_id}")
        result = await self.repo.remove_reaction(message_id, reaction, author)
        if result > 0:
            event_data = Reaction(
                message_id=message_id,
                author=author,
                reaction=reaction
            )
            await self.kafka_producer.remove_reaction(event_data)
        else:
            raise ReacionNotAdded()
