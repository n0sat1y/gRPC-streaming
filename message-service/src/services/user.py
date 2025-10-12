from loguru import logger

from src.repositories.user import UserRepository
from src.models.replications import UserReplica
from src.schemas.user import UserData, IdSchema


class UserService():
    def __init__(self):
        self.repo = UserRepository()

    async def create(self, data: UserData):
        logger.info(f"Создаем пользователя {data.id}")
        
        new_user = await self.repo.upsert_data(data.model_dump())
        logger.info(f"Пользователь создан: {new_user}")

    async def deactivate(self, data: IdSchema):
        logger.info(f"Деактивируем пользователя {data.id}")
        
        new_user = await self.repo.deactivate(data.id)
        logger.info(f"Пользователь деактивирован: {new_user}")

