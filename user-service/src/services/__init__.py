import grpc
from loguru import logger

from sqlalchemy.exc import IntegrityError
from src.repositories import UserRepository

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
