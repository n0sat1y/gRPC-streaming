import asyncio
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.repositories import ChatRepository
from src.models import ChatModel
from src.services.rpc import RpcService
from src.schemas import *


class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
        self.rpc = RpcService()

    async def get(self, id: int, context: grpc.aio.ServicerContext):
        try:
            chat = await self.get_model(id, context)
            chat = GetFullChatData.model_validate(chat)

            tasks = [self.rpc.get_user_by_id(member.user_id) for member in chat.members]
            usernames = await asyncio.gather(*tasks)

            full_members = []
            for member, username in zip(chat.members, usernames):
                full_members.append(
                    ChatMemberSchema(user_id=member.user_id, username=username)
                )

            return GetFullChatData(
                name=chat.name,
                created_at=chat.created_at,
                members=full_members
            )
        except Exception as e:
            raise e
        
    async def get_model(self, id: int, context: grpc.aio.ServicerContext) -> ChatModel:
        try:
            chat = await self.repo.get(id)
            if not chat:
                logger.warning(f"Не получилось найти чат: {id}")
                await context.abort(
                    code=grpc.StatusCode.NOT_FOUND,
                    details='Chat not found'
                )
            logger.info(f"Чат найден: {id}")

            return chat
        except Exception as e:
            raise e
        

    async def get_user_chats(self, user_id: int, context: grpc.aio.ServicerContext) -> list[GetChatData]:
        try:
            chats = await self.repo.get_by_user_id(user_id)
            if not chats:
                logger.info(f"Чаты пользователя не найдены: {user_id}")
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    details='User chats not found'
                )
            result = [GetChatData.model_validate(model) for model in chats]
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении чатов пользователя {user_id=}", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            )            

    async def create(self, data: dict, context: grpc.aio.ServicerContext):
        try:
            members = data.pop('members')
            chat = await self.repo.create(data, members)
            return chat
        except IntegrityError as e:
            logger.warning(f"Чат уже создан:")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details='Chat already exists'
            )
        except Exception as e:
            logger.error("Ошибка при создании чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            )

    async def add_members(self, chat_id: int, members: list, context: grpc.aio.ServicerContext):
        try:
            if not members:
                logger.warning('Новые пользователи не были переданы')
                await context.abort(
                    grpc.StatusCode.DATA_LOSS,
                    details='Members not added'
                )

            chat = await self.repo.get(chat_id)
            if not chat:
                logger.warning(f"Не получилось найти чат: {id}")
                await context.abort(
                    code=grpc.StatusCode.NOT_FOUND,
                    details='Chat not found'
                )
            logger.info(f"Чат найден: {id}")

            if not await self.repo.add_members(chat, members):
                await context.abort(
                    grpc.StatusCode.INTERNAL,
                    details='Failed to add members'
                )
            return chat
        
        except IntegrityError as e:
            logger.warning(f"Чат уже создан:")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details='Members already added'
            ) 

        except Exception as e:
            logger.error("Ошибка при создании чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            )

    async def delete(self, chat_id: int, context: grpc.aio.ServicerContext):
        try:
            await self.repo.delete(chat_id)

            if await self.repo.get(chat_id):
                logger.warning(f"Не удалось удалить чат {chat_id=}")
                await context.abort(
                    grpc.StatusCode.ABORTED,
                    details='Failed to delete chat'
                )

            logger.info(f"Удален чат {chat_id=}")
            return 'Successfully deleted'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            ) 

    async def delete_user_from_chat(self, user_id: int, chat_id: int, context: grpc.aio.ServicerContext):
        try:
            user_chats = await self.get_user_chats(user_id, context)
            if not chat_id in [chat.id for chat in user_chats]:
                logger.warning(f'Чат {chat_id=} не найден в существующих чатах пользователя {user_id=}')
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    details='This chat not found in user chats'
                )
            await self.repo.delete_user_from_chat(user_id, chat_id)
            logger.info(f"Пользователь {user_id=} был удален из чата {chat_id=}")

            chat = await self.get_model(chat_id, context)
            if not chat.members:
                logger.info(f"Был удален последний пользователь. Удаление чата {chat_id=}")
                await self.delete(chat_id, context)

            return 'Successfully deleted'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            ) 
        

