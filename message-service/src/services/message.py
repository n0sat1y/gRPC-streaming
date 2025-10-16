import grpc
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
            tmp_message_id: str, 
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
            if member.is_active == True and member.user_id != user_id
        ]

        event_data = MessageData(
            id=str(message.id),
            chat_id= message.chat_id,
            content=message.content,
            sender=UserData(
                id=user.user_id,
                username=user.username
            ),
            tmp_message_id=tmp_message_id,
            created_at=message.created_at
        )
        await broker.publish(
            CreatedMessageEvent(
                recievers=active_recievers,
                data=event_data
            ), 'message.event')
        logger.info(f"Уведомление о создании сообщения {message.id} отправлено")

        return message
    
    async def delete_chat_messages(self, chat_id: int):
        logger.info(f"Удаляем сообщения чата {chat_id}")
        deleted_count = await self.repo.delete_chat_messages(chat_id)
        logger.info(f"Удалены {deleted_count} сообщения чата: {chat_id=}")



