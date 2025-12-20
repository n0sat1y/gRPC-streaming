from loguru import logger

from src.repositories.user import UserRepository
from src.models.replications import UserReplica
from src.schemas.user import UserData, IdSchema


class UserService():
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get(self, user_id: int) -> UserReplica:
        logger.info(f'Получаем пользователя {user_id}')
        user = await self.repo.get(user_id)
        logger.info(f'Получен пользователь {user_id}')
        return user
    
    async def get_multiple(self, ids: list[int]) -> list[UserReplica]:
        str_list = ', '.join(str(x) for x in ids)
        logger.info(f'Получаем пользователей {str_list}')
        users = await self.repo.get_multiple(ids)
        logger.info(f'Получены пользователи {str_list}')
        return users

    async def create(self, data: UserData):
        logger.info(f"Создаем пользователя {data.id}")
        
        new_user = await self.repo.upsert_data(data.model_dump())
        logger.info(f"Пользователь создан: {new_user}")

    async def deactivate(self, data: IdSchema):
        logger.info(f"Деактивируем пользователя {data.id}")
        
        new_user = await self.repo.deactivate(data.id)
        logger.info(f"Пользователь деактивирован: {new_user}")

