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
    
    async def get_by_username(self, username: str, context: grpc.aio.ServicerContext):
        user = await self.repo.get_by_username(username)
        if not user:
            logger.warning(f'User not found {id}')
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                'User not found'
            )
        logger.info(f'Найден пользователь: {user.username}')
        return user
    
    async def get_multiple(self, ids: list, context: grpc.aio.ServicerContext):
        ids = [x.id for x in ids]
        users = await self.repo.get_multiple(ids)
        missed = []
        if not len(users) == len(ids):
            found = [x.id for x in users]
            missed = [x for x in ids if x not in found]
            logger.warning(f"Не найдены пользователи: {missed=}")
        else:
            logger.info(f"Найдены пользователи: {ids=}")
        return users, missed

    
    async def create(self, data: dict, context: grpc.aio.ServicerContext):
        try:
            username = data['username']
            logger.info(f'Создаем пользователя: {username}')
            new_user = await self.repo.create(data)
            logger.info(f'Создан пользователь: {username}')
            return new_user
        except IntegrityError as e:
            logger.error(f"Попытка повторно создать пользователя: {username}")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                'User already exists'
            )
    
    async def delete(self, user_id: int, context:grpc.aio.ServicerContext):
        try:
            result = await self.repo.delete(user_id)

            if result == 0:
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
