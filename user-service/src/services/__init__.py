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
                'Idi nahuy'
            )
        logger.info(f'Found user: {user.username}')
        return user
    
    async def create(self, data: dict, context: grpc.aio.ServicerContext):
        try:
            new_user = await self.repo.create(data)
            return new_user
        except IntegrityError as e:
            await context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                'Idi nahuy x2'
            )

    #Здесь будут потом вызываться репозитории
