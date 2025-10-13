import grpc
from collections import defaultdict
from loguru import logger
from faststream.kafka import KafkaBroker

from src.repositories.message import MessageRepository
from src.services.user import UserService
from src.services.chat import ChatService
from src.models import Message


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
    
    async def insert(self, user_id: int, chat_id: int, content: str, context: grpc.aio.ServicerContext,  broker: KafkaBroker):
        errors = []
        if not (chat := await self.chat_service.get(chat_id)):
            errors.append('chat_id')
        if not (user := await self.user_service.get(user_id) or user.is_active):
            errors.append('user_id')
        elif not user.user_id in chat.members:
            print(chat.members)
            errors.append('user not is chat member')

        if errors:
            logger.warning(f"Неверные данные: {', '.join(errors)}")
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=f"Wrong data: {', '.join(errors)}"
            )

        message = Message(user_id=user_id, chat_id=chat_id, content=content)
        message = await self.repo.insert(message)
        logger.info(f"Добавлено сообщение {message.id=} в {chat_id=}")

        print(message.__dict__)
        await broker.publish({
            'event_type': 'MessageCreated',
            'data': {
                'id': str(message.id),
                'chat_id': message.chat_id,
                'content': message.content,
                'created_at': message.created_at
            }
        }, 'message.event')
        logger.info(f"Уведомление о создании сообщения {message.id} отправлено")

        return message
    
    async def delete_chat_messages(self, chat_id: int):
        logger.info(f"Удаляем сообщения чата {chat_id}")
        deleted_count = await self.repo.delete_chat_messages(chat_id)
        logger.info(f"Удалены {deleted_count} сообщения чата: {chat_id=}")

class ConnectionService:
    def __init__(self):
        self.active_connections = defaultdict(list)
        
    def connect(self, chat_id: int, stream):
        self.active_connections[chat_id].append(stream)
    
    def disconnect(self, chat_id: int, stream):
        self.active_connections[chat_id].remove(stream)

    async def broabcast(self, chat_id: int, message):
        for stream in self.active_connections[chat_id]:
            await stream.write(message)



