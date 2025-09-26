import asyncio
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.repositories import ChatRepository
from src.services.rpc import RpcService
from src.schemas import *


class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
        self.rpc = RpcService()

    async def get(self, id: int, context: grpc.aio.ServicerContext):
        try:
            chat = await self.repo.get(id)
            if not chat:
                logger.warning(f"Не получилось найти чат: {id}")
                await context.abort(
                    code=grpc.StatusCode.NOT_FOUND,
                    details='Chat not found'
                )
            logger.info(f"Чат найден: {id}")

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

    async def get_user_chats(self, user_id: int, context: grpc.aio.ServicerContext):
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

        

