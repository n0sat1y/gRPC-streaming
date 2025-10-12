from datetime import datetime
import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError
from faststream.kafka import KafkaBroker

from src.repositories.chat import ChatRepository
from src.services.user import UserService
from src.models import ChatModel
from src.schemas.chat import Chat
from src.schemas.message import MessageData

class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
        self.user_service = UserService()
        
    async def get(self, id: int, context: grpc.aio.ServicerContext) -> ChatModel:
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
            return chats
        except Exception as e:
            logger.error(f"Ошибка при получении чатов пользователя {user_id=}", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            )     

    async def get_multiple_users(self, members: list[dict], context: grpc.aio.ServicerContext):
        ids = [x['id'] for x in members]
        found, missed = await self.user_service.get_multiple(ids)
        if missed:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details=f"Missed users: {', '.join(str(i) for i in missed)}"
            )
        return found

    async def create(self, data: dict, context: grpc.aio.ServicerContext, broker: KafkaBroker):
        try:
            members = data.pop('members')
            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members, context)
            
            chat = await self.repo.create(data, members)
            
            members = [c.user_id for c in chat.members]
            await broker.publish({
                'event_type': 'ChatCreated',
                'data': {
                    'id': chat.id,
                    'members': members
                }
            }, 'chat.events')
            logger.info(f"Уведомление о создании чата {chat.id} отправлено")

            return chat
        except IntegrityError as e:
            logger.warning(f"Чат уже создан:")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details='Chat already exists'
            )
        except Exception as e:
            logger.error("Ошибка при создании чата")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            )

    async def update(self, chat_id: int, data: dict, context: grpc.aio.ServicerContext):
        try:
            chat = await self.get(chat_id, context)

            if not (chat := await self.repo.update(chat, data)):
                logger.error(f"Не удалось обновить чат {chat_id}")
                await context.abort(
                    grpc.StatusCode.INTERNAL,
                    details='Failed to update chat'
                )

            return chat

        except Exception as e:
            logger.error("Ошибка при создании чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            )

    async def add_members(self, chat_id: int, members: list[dict], context: grpc.aio.ServicerContext, broker: KafkaBroker):
        try:
            chat = await self.get(chat_id, context)
        
            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members, context)
                
            if not (chat := await self.repo.add_members(chat, members)):
                logger.error(f"Не удалось добваить пользователей в чат {chat_id}")
                await context.abort(
                    grpc.StatusCode.INTERNAL,
                    details='Failed to add members to chat'
                )
            members = [c.user_id for c in chat.members]
            await broker.publish({
                'event_type': 'ChatUpdated',
                'data': {
                    'id': chat.id,
                    'members': members
                }
            }, 'chat.events')
            logger.info(f"Уведомление об обновлении чата {chat_id} отправлено")

            return chat
        
        except IntegrityError as e:
            logger.warning(f"Участники уже добавлены: {e}")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                details=f'Members already added'
            ) 

        except Exception as e:
            logger.error(f"Ошибка при создании чата, {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            )

    async def update_chat_last_message(self, data: MessageData):
        chat = await self.repo.get(data.chat_id)
        if not chat:
            logger.error(f"Не удалось найти чат: {data.chat_id}")
        logger.info(f"Обновляем чат: {data.chat_id}")
        await self.repo.update_chat_last_message(chat, data.content, data.created_at)
        logger.info(f"Чат обновлен: {data.chat_id}")

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

            await broker.publish({
                'event_type': 'ChatDeleted',
                'data': {
                    'id': chat_id
                }
            }, 'chat.events')
            logger.info(f"Отправлено уведомление об удалении чата {chat_id=}")

            return 'Success'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            ) 

    # async def delete_user_chats(self, user_id: int, broker: KafkaBroker):
    #     try:
    #         count = await self.repo.delete_user_chats(user_id)
    #         logger.info(f"Удалены чаты пользователя {user_id}: {count=}")
    #         return
    #     except Exception as e:
    #         logger.error("Ошибка при удалении пользователя из чата", e)

    async def delete_user_from_chat(self, user_id: int, chat_id: int, context: grpc.aio.ServicerContext, broker: KafkaBroker):
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

            chat = await self.get(chat_id, context)
            if not chat.members:
                logger.info(f"Был удален последний пользователь. Удаление чата {chat_id=}")
                await self.delete(chat_id, context, broker)
            else:
                members = [c.user_id for c in chat.members]
                await broker.publish({
                    'event_type': 'ChatUpdated',
                    'data': {
                        'id': chat.id,
                        'members': members
                    }
                }, 'chat.events')
                logger.info(f"Уведомление об обновлении чата {chat.id} отправлено")

            return 'Success'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            ) 
