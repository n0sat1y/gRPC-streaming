import asyncio
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError
from faststream.kafka import KafkaBroker

from src.repositories import ChatRepository
from src.models import ChatModel
from src.services.rpc import RpcUserService
from src.schemas import *


class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
        self.rpc = RpcUserService()

    async def get(self, id: int, context: grpc.aio.ServicerContext):
        try:
            chat = await self.get_model(id, context)
            return chat
            # chat = GetFullChatData.model_validate(chat)

            # return GetFullChatData(
            #     name=chat.name,
            #     created_at=chat.created_at,
            #     members=chat.members
            # )
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
        

    async def get_user_chats(self, user_id: int, context: grpc.aio.ServicerContext) -> list[ChatModel]:
        try:
            chats = await self.repo.get_by_user_id(user_id)
            if not chats:
                logger.info(f"Чаты пользователя не найдены: {user_id}")
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    details='User chats not found'
                )
            # result = [GetChatData.model_validate(model) for model in chats]
            return chats
        except Exception as e:
            logger.error(f"Ошибка при получении чатов пользователя {user_id=}", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            )            

    async def create(self, data: dict, context: grpc.aio.ServicerContext):
        try:
            members = data.pop('members')
            if not members:
                logger.warning('Новые пользователи не были переданы')
                await context.abort(
                    grpc.StatusCode.DATA_LOSS,
                    details='Members not added'
                )
            users_data = await self.rpc.get_multiple(members)
            if users_data.status == 'Missed':
                logger.warning(f"Не найдены пользователи: {users_data.missed=}")
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    details=f"Missed users: {', '.join(str(x.id) for x in users_data.missed)}"
                )
            chat = await self.repo.create(data, members)
            return chat
        except grpc.RpcError as e:
                logger.error(e.details)
                raise e
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
            try:
                users_data = await self.rpc.get_multiple(members)
                if users_data.status == 'Missed':
                    logger.warning(f"Не найдены пользователи: {users_data.missed=}")
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        details=f"Missed users: {', '.join(str(x) for x in users_data.missed)}"
                    )
            except grpc.RpcError as e:
                logger.error(e.details)
                raise e

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

    async def delete(self, chat_id: int, context: grpc.aio.ServicerContext, broker: KafkaBroker):
        try:
            result = await self.repo.delete(chat_id)

            if result == 0:
                logger.warning(f"Попытка удалить несуществующий чат {chat_id=}")
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    details='Chat not found'
                )

            logger.info(f"Удален чат {chat_id=}")

            await broker.publish(chat_id, 'ChatDeleted')
            logger.info(f"Отправлено уведомление об удалении чата {chat_id=}")

            return 'Successfully deleted'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            ) 

    async def delete_user_chats(self, user_id: int):
        try:
            count = await self.repo.delete_user_chats(user_id)
            logger.info(f"Удалены чаты пользователя {user_id}: {count=}")
            return
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)

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

    
        

