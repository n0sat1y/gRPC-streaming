from datetime import datetime
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError
from faststream.kafka import KafkaBroker

from src.repositories.chat import ChatRepository
from src.services.user import UserService
from src.core.interfaces.services import IChatService
from src.models import ChatModel, ChatMemberModel, UserReplicaModel
from src.schemas.chat import *
from src.schemas.message import MessageData
from src.exceptions.chat import *
from src.exceptions.user import *
from src.enums.enums import ChatTypeEnum
from src.dto.chat import *
from src.routers.kafka.producer import KafkaPublisher


class ChatService(IChatService):
    def __init__(
        self,
        producer: KafkaPublisher,
        repo: ChatRepository,
        user_service: UserService,
    ):
        self.repo = repo
        self.user_service = user_service
        self.producer = producer
        
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

    async def get_multiple_users(self, members: list) -> List[UserReplicaModel]:
        found, missed = await self.user_service.get_multiple(members)
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
    
    async def get_or_create_private(self, current_user: int, target_user: int) -> ChatModel:
        logger.info(f"Проверяем наличие чата в бд: {current_user=}, {target_user=}")
        if chat := await self.repo.get_private(current_user, target_user):
            logger.info(f"Чат найден: {chat.id}")
            return chat
        logger.info(f"Чат не найден, создаем новый")

        chat = await self.repo.create_private(current_user, target_user)
        logger.info(f"Чат создан: {chat.id}")

        members = [current_user, target_user]
        
        event_data = ChatDataBase(id=chat.id, members=members)
        await self.producer.create(event_data)

        return chat

    async def create_group(self, data: CreateGroupDTO):
        try:
            logger.info(f"Проверяем наличие пользователей в бд")
            members = [x.id for x in data.members]
            await self.get_multiple_users(members)
            
            chat = await self.repo.create_group(data)
            
            event_data = ChatDataBase(id=chat.id, members=members)
            await self.producer.create(data=event_data)

            return chat
        except IntegrityError as e:
            logger.warning(f"Чат уже создан:")
            raise ChatAlreadyExistsError(data['name'])

    async def update(self, data: UpdateGroupDTO):
        chat = await self.get(data.id)
        if not (chat := await self.repo.update(chat, data)):
            logger.error(f"Не удалось обновить чат {data.id}")
            raise ChatUpdateFailed()
        return chat
    
    async def update_last_read_message(
            self, 
            chat_id: int, 
            user_id: int, 
            last_read_message_id: str
        ):
        chat_member = await self.get_chat_member(chat_id, user_id)
        if not (chat_member := await self.repo.update_last_read_message(chat_member, last_read_message_id)):
            logger.error(f"Не удалось обновить чат {chat_id}")
            raise ChatMemberUpdateFailed()
        return chat_member

    async def add_members(self, chat_id: int, members: list):
        try:
            chat = await self.get(chat_id)
        
            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members)
                
            if chat.chat_type != ChatTypeEnum.GROUP:
                logger.warning(f"Попытка добавить пользователей в личный чат")
                raise AddMembersAborted()
            if not (chat := await self.repo.add_members(chat, members)):
                logger.error(f"Не удалось добваить пользователей в чат {chat_id}")
                raise AddMembersFailed()
            members = [c.user_id for c in chat.members]

            event_data = ChatDataBase(id=chat.id, members=members)
            await self.producer.update(data=event_data)
            
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

    async def delete(self, chat_id: int):
        result = await self.repo.delete(chat_id)

        if result == 0:
            logger.warning(f"Попытка удалить несуществующий чат {chat_id=}")
            raise ChatNotFoundError(chat_id)

        logger.info(f"Удален чат {chat_id=}")

        await self.producer.delete(chat_id=chat_id)
        
        return 'Success'

    # async def delete_user_chats(self, user_id: int):
    #     try:
    #         count = await self.repo.delete_user_chats(user_id)
    #         logger.info(f"Удалены чаты пользователя {user_id}: {count=}")
    #         return
    #     except Exception as e:
    #         logger.error("Ошибка при удалении пользователя из чата", e)

    async def delete_user_from_chat(self, user_id: int, chat_id: int):
        user_chats = await self.get_user_chats(user_id)
        if not chat_id in [chat.id for chat in user_chats]:
            logger.warning(f'Чат {chat_id=} не найден в существующих чатах пользователя {user_id=}')
            raise UserChatNotFound()
        
        await self.repo.delete_user_from_chat(user_id, chat_id)
        logger.info(f"Пользователь {user_id=} был удален из чата {chat_id=}")

        chat = await self.get(chat_id)
        if not chat.members:
            logger.info(f"Был удален последний пользователь. Удаление чата {chat_id=}")
            await self.delete(chat_id, self.broker)
        else:
            members = [c.user_id for c in chat.members]
            event_data = ChatDataBase(id=chat.id, members=members)
            await self.producer.update(data=event_data)
        return 'Success'
