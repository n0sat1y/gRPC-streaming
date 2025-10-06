import grpc
from loguru import logger

from sqlalchemy.exc import IntegrityError
from src.repositories import UserRepository
from src.kafka import broker

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    async def get_by_id(self, id: int, context: grpc.aio.ServicerContext):
        user = await self.repo.get(id)
        if not user:
            logger.warning(f'User not found {id}')
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                'User not found'
            )
        logger.info(f'Найден пользователь: {user.username}')
        return user
    
    async def create(self, data: dict, context: grpc.aio.ServicerContext):
        try:
            new_user = await self.repo.create(data)
            username = data['username']
            logger.info(f'Создан пользователь: {username}')
            return new_user
        except IntegrityError as e:
            logger.error(f"Попытка повторно создать пользователя: {username}")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                'User already exists'
            )

    async def get_or_create(self, username: str, context:grpc.aio.ServicerContext):
        user = await self.repo.get_by_username(username)
        if not user:
            logger.warning(f'Не удалось получить пользователя: {username}. Создаем нового.')
            user = await self.create({'username': username}, context)
        logger.info(f"Получен пользователь: {username}")
        return user
    
    async def delete(self, user_id: int, context:grpc.aio.ServicerContext):
        try:
            await self.repo.delete(user_id)

            if await self.repo.get(user_id):
                logger.warning(f"Не удалось удалить пользователя {user_id=}")
                await context.abort(
                    grpc.StatusCode.ABORTED,
                    details='Failed to delete user'
                )
            logger.info(f"Удален пользователь {user_id=}")

            await broker.publish(user_id, 'UserDeleted')
            logger.info(f'Отправлено уведомление об удалении пользователя {user_id=}')

            return 'Successfully deleted'
        except Exception as e:
            logger.error("Ошибка при удалении пользователя", e)
            await context.abort(
                grpc.StatusCode.INTERNAL,
                details=e
            ) 
