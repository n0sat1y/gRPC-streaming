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
            logger.info(f'Создан пользователь: {data['username']}')
            return new_user
        except IntegrityError as e:
            logger.error(f"Попытка повторно создать пользователя: {data['username']}")
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                'User already exists'
            )

    #Здесь будут потом вызываться репозитории
