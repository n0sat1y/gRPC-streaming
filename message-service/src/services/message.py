import grpc
import uuid
from collections import defaultdict
from loguru import logger
from faststream.kafka import KafkaBroker

from src.repositories.message import MessageRepository
from src.services.user import UserService
from src.services.chat import ChatService
from src.models import Message
from src.exceptions.message import *
from src.schemas.message import *


class MessageService:
    def __init__(self):
        self.repo = MessageRepository()
        self.user_service = UserService()
        self.chat_service = ChatService()

    async def get(self, message_id: str) -> Message:
        logger.info(f"Получаем сообщение {message_id}")
        message = await self.repo.get(message_id)
        if not message:
            logger.warning(f"Не найдено сообщение {message_id}")
            raise MessageNotFoundError(message_id=message_id)
        return message

    async def get_all(self, chat_id: int):
        result = await self.repo.get_all(chat_id)
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
            broker: KafkaBroker
        ):
        errors = []
        if not (chat := await self.chat_service.get(chat_id)):
            errors.append('chat_id')
        user = await self.user_service.get(user_id)
        if not user or not user.is_active:
            errors.append('user_id')
        elif not user.user_id in chat.members:
            print(chat.members)            
            errors.append('user not is chat member')

        if errors:
            err_str = ', '.join(errors)
            logger.warning(f"Неверные данные: {err_str}")
            raise DataLossError(err_str)

        message = Message(user_id=user_id, chat_id=chat_id, content=content)
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
        await broker.publish(
            CreatedMessageEvent(
                recievers=active_recievers,
                data=event_data,
                request_id=request_id,
                event_id=str(uuid.uuid4()),
                sender_id=sender_id,
            ), 'message.event')
        logger.info(f"Уведомление о создании сообщения {message.id} отправлено")

        return message
    
    async def update(
        self, 
        message_id: str, 
        new_content: str, 
        request_id: str, 
        sender_id: int,
        broker: KafkaBroker
    ) -> Message:
        logger.info(f"Обновляем сообщение {message_id}")

        message = await self.get(message_id)
        message = await self.repo.update(message, new_content)
        logger.info(f"Обновлено сообщение: {message_id}")

        active_recievers = await self.chat_service.get_active_members(chat_id=message.chat_id)
        event_data = UpdateMessagePayload(id=str(message.id), content=message.content)
        await broker.publish(
            UpdateMessageEvent(
                recievers=active_recievers,
                data=event_data,
                request_id=request_id,
                event_id=str(uuid.uuid4()),
                sender_id=sender_id,
            ), 'message.event'
        )
        logger.info(f"Уведомление об обновлении сообщения {message.id} отправлено")
        return message
    
    async def delete(
        self, 
        message_id: str, 
        request_id: str, 
        sender_id: int,
        broker: KafkaBroker
    ):
        logger.info(f"Удаляем сообщение {message_id}")
        message = await self.get(message_id)
        await self.repo.delete(message)
        logger.info(f"Удалено сообщение {message_id}")

        recievers = await self.chat_service.get_active_members(message.chat_id)
        await broker.publish(
            DeleteMessageEvent(
                recievers=recievers,
                data=MessageIdPayload(id=str(message_id)),
                request_id=request_id,
                event_id=str(uuid.uuid4()),
                sender_id=sender_id,
            ), 'message.event'
        )
        logger.info(f"Уведомление об удалении сообщения {message.id} отправлено")
    
    async def delete_chat_messages(self, chat_id: int):
        logger.info(f"Удаляем сообщения чата {chat_id}")
        deleted_count = await self.repo.delete_chat_messages(chat_id)
        logger.info(f"Удалены {deleted_count} сообщения чата: {chat_id=}")


    async def mark_as_read(
            self, 
            chat_id: int, 
            user_id: int, 
            message_id: str,
            broker: KafkaBroker
        ):
        logger.info(f"Обновляем последнее прочитанное сообщение")

        previous_read_message = await self.repo.get_last_read_message(chat_id=chat_id, user_id=user_id)
        print(previous_read_message)
        await self.repo.set_last_read_message(chat_id, user_id, message_id)
        logger.info(f"Обновили счетчик последнего прочитанного сообщения")

        changed_messages = await self.repo.mark_as_read(
            previous_message_read=previous_read_message,
            last_read_message=message_id,
            read_by=user_id
        )
        if changed_messages:
            event_data = [SlimMessageData(id=str(message.id), sender_id=message.user_id) for message in changed_messages]
            await broker.publish(
                MessagesReadedEvent(
                    data=event_data,
                    event_id=str(uuid.uuid4())
                ), 'message.was_read'
            )
            logger.info(f"Уведомление о прочтении сообщений отправлено")

        logger.info(f"Последнее прочитанное сообщение пользователя {user_id} обновлено")
