from datetime import datetime
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError
from faststream.kafka import KafkaBroker

from src.repositories.chat import ChatRepository
from src.services.user import UserService
from src.models import ChatModel, ChatMemberModel
from src.schemas.chat import *
from src.schemas.message import MessageData
from src.exceptions.chat import *
from src.exceptions.user import *

class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
        self.user_service = UserService()
        
    async def get(self, id: int) -> ChatModel:
        chat = await self.repo.get(id)
        if not chat:
            logger.warning(f"Не получилось найти чат: {id}")
            raise ChatNotFoundError(id)
        logger.info(f"Чат найден: {id}")

        return chat       

    async def get_user_chats(self, user_id: int) -> list[ChatModel]:
        chats = await self.repo.get_by_user_id(user_id)
        if not chats:
            logger.info(f"Чаты пользователя не найдены: {user_id}")
            raise ChatNotFoundError(user_id)
        return chats

    async def get_multiple_users(self, members: list[dict]):
        ids = [x['id'] for x in members]
        found, missed = await self.user_service.get_multiple(ids)
        if missed:
            raise UsersNotFoundError(missed)
        return found
    
    async def get_chat_member(self, chat_id: int, user_id: int) -> ChatMemberModel:
        chat_member = await self.repo.get_chat_member(chat_id, user_id)
        if not chat_member:
            logger.warning(f"Пользователь {user_id} не найден в участниках чата {chat_id}")
            raise ChatMemberNotFound()
        logger.info(f"Найден пользователь {user_id}")
        return chat_member

    async def create(self, data: dict, broker: KafkaBroker):
        try:
            members = data.pop('members')
            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members)
            
            chat = await self.repo.create(data, members)
            
            members = [c.user_id for c in chat.members]
            event_data = ChatDataBase(id=chat.id, members=members)
            await broker.publish(CreateChatEvent(data=event_data), 'chat.events')
            logger.info(f"Уведомление о создании чата {chat.id} отправлено")

            return chat
        except IntegrityError as e:
            logger.warning(f"Чат уже создан:")
            raise ChatAlreadyExistsError(data['name'])
        except Exception as e:
            logger.opt(exception=True).error(f"Ошибка при создании чата, {e}")
            raise e

    async def update(self, chat_id: int, data: dict):
        chat = await self.get(chat_id)
        if not (chat := await self.repo.update(chat, data)):
            logger.error(f"Не удалось обновить чат {chat_id}")
            raise ChatUpdateFailed()
        return chat

    async def add_members(self, chat_id: int, members: list[dict], broker: KafkaBroker):
        try:
            chat = await self.get(chat_id)
        
            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members)
                
            if not (chat := await self.repo.add_members(chat, members)):
                logger.error(f"Не удалось добваить пользователей в чат {chat_id}")
                raise AddMembersFailed()
            members = [c.user_id for c in chat.members]

            event_data = ChatDataBase(id=chat.id, members=members)
            await broker.publish(UpdateChatEvent(data=event_data), 'chat.events')
            logger.info(f"Уведомление об обновлении чата {chat_id} отправлено")

            return chat
        
        except IntegrityError as e:
            logger.warning(f"Участники уже добавлены: {e}")
            raise MembersAlreadyAdded()


    async def update_chat_last_message(self, data: MessageData):
        chat = await self.repo.get(data.chat_id)
        if not chat:
            logger.error(f"Не удалось найти чат: {data.chat_id}")
        logger.info(f"Обновляем чат: {data.chat_id}")
        await self.repo.update_chat_last_message(chat, data.content, data.created_at)
        logger.info(f"Чат обновлен: {data.chat_id}")

    async def delete(self, chat_id: int, broker: KafkaBroker):
        result = await self.repo.delete(chat_id)

        if result == 0:
            logger.warning(f"Попытка удалить несуществующий чат {chat_id=}")
            raise ChatNotFoundError(chat_id)

        logger.info(f"Удален чат {chat_id=}")

        await broker.publish(DeleteChatEvent(
            data=ChatIdBase(id=chat_id)), 
            'chat.events'
        )
        logger.info(f"Отправлено уведомление об удалении чата {chat_id=}")

        return 'Success'

    # async def delete_user_chats(self, user_id: int, broker: KafkaBroker):
    #     try:
    #         count = await self.repo.delete_user_chats(user_id)
    #         logger.info(f"Удалены чаты пользователя {user_id}: {count=}")
    #         return
    #     except Exception as e:
    #         logger.error("Ошибка при удалении пользователя из чата", e)

    async def delete_user_from_chat(self, user_id: int, chat_id: int, broker: KafkaBroker):
        user_chats = await self.get_user_chats(user_id)
        if not chat_id in [chat.id for chat in user_chats]:
            logger.warning(f'Чат {chat_id=} не найден в существующих чатах пользователя {user_id=}')
            raise UserChatNotFound()
        
        await self.repo.delete_user_from_chat(user_id, chat_id)
        logger.info(f"Пользователь {user_id=} был удален из чата {chat_id=}")

        chat = await self.get(chat_id)
        if not chat.members:
            logger.info(f"Был удален последний пользователь. Удаление чата {chat_id=}")
            await self.delete(chat_id, broker)
        else:
            members = [c.user_id for c in chat.members]
            event_data = ChatDataBase(id=chat.id, members=members)
            await broker.publish(UpdateChatEvent(data=event_data), 'chat.events')
            logger.info(f"Уведомление об обновлении чата {chat.id} отправлено")

        return 'Success'
