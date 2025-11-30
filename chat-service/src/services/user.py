from loguru import logger
from typing import List

from src.core.interfaces.repositories import IUserRepository
from src.models import UserReplicaModel
from src.schemas.user import UserData
from src.core.interfaces.services import IUserService

class UserService(IUserService):
    def __init__(
        self,
        repo: IUserRepository
    ):
        self.repo = repo

    async def get(self, user_id: int):
        try:
            user = await self.repo.get(user_id)
            logger.info(f"Пользователь получен {user.username}")
            return user
        except Exception as e:
            logger.error(f"Ошибка во время получения пользователея {user_id}: {e}")

    async def get_multiple(self, ids: list[int]) -> tuple[list[UserReplicaModel], list[UserReplicaModel]]:
        users = await self.repo.get_multiple(ids)
        missed = []
        if not len(users) == len(ids):
            found = [x.id for x in users]
            missed = [x for x in ids if x not in found]
            logger.warning(f"Не найдены пользователи: {missed=}")
        else:
            logger.info(f"Найдены пользователи: {ids=}")
        return users, missed

    async def create_or_update(self, data: UserData):
        try:
            logger.info(f"Создание пользователя {data.username}")
            await self.repo.upsert(data.model_dump())
            logger.info(f"Пользователь создан {data.username}")
        except Exception as e:
            logger.error(f"Ошибка во время изменения реплики пользователей: {e}")

    async def deactivate(self, id: int):
        try:
            logger.info(f"Деактивация пользователя {id}")
            await self.repo.deactivate(id)
            logger.info(f"Пользователь деактивирован {id}")
        except Exception as e:
            logger.error(f"Ошибка во время удаления пользователя {id}: {e}")

