import grpc
from loguru import logger
from sqlalchemy.exc import IntegrityError
from faststream.kafka import KafkaBroker

from src.repositories.chat import ChatRepository
from src.services.user import UserService
from src.models import ChatModel
from src.schemas.chat import Chat

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
            if not members:
                logger.warning('Новые пользователи не были переданы')
                await context.abort(
                    grpc.StatusCode.DATA_LOSS,
                    details='Members not added'
                )

            logger.info(f"Проверяем наличие пользователей в бд")
            await self.get_multiple_users(members, context)
            
            chat = await self.repo.create(data, members)

            await broker.publish(Chat.model_validate(chat).model_dump(), 'ChatCreated')
            logger.info(f"Уведомление о создании чата {chat.id} отправлено")

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
                details=str(e)
            )

    async def update(self, chat_id: int, data: list, context: grpc.aio.ServicerContext, broker: KafkaBroker):
        try:
            chat = await self.repo.get(chat_id)
            if not chat:
                logger.warning(f"Не получилось найти чат: {id}")
                await context.abort(
                    code=grpc.StatusCode.NOT_FOUND,
                    details='Chat not found'
                )
            logger.info(f"Чат найден: {id}")

            if 'members' in data:
                logger.info(f"Проверяем наличие пользователей в бд")
                await self.get_multiple_users(data['members'], context)

            if not await self.repo.update(chat, data):
                logger.error(f"Не удалось обновить чат {chat_id}")
                await context.abort(
                    grpc.StatusCode.INTERNAL,
                    details='Failed to update chat'
                )

            await broker.publish({'chat_id': chat_id, 'data': data}, 'ChatUpdated')
            logger.info(f"Уведомление об обновлении чата {chat.id} отправлено")

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
                details=str(e)
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
                details=str(e)
            ) 

    async def delete_user_chats(self, user_id: int):
        try:
            count = await self.repo.delete_user_chats(user_id)
            logger.info(f"Удалены чаты пользователя {user_id}: {count=}")

            return
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)

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
                await self.delete(chat_id, context)

            await broker.publish({'user_id': user_id, 'chat_id': user_id}, 'UserFromChatDeleted')
            logger.info(f"Уведомление о создании чата {chat.id} отправлено")

            return 'Successfully deleted'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя из чата", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=str(e)
            ) 
