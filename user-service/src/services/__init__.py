from loguru import logger
from sqlalchemy.exc import IntegrityError
from dataclasses import asdict

from src.repositories import UserRepository
from src.exceptions.user import (
    UserNotFoundError, UserAlreadyExistsError
)
from src.schemas.user import *
from src.dto.user import UpdateUserDataDTO
from src.models import UserModel
from src.routers.kafka.producer import KafkaPublisher

class UserService:
    def __init__(
        self, 
        repo: UserRepository,
        producer: KafkaPublisher,
    ):
        self.repo = repo
        self.producer = producer 

    async def get_by_id(self, id: int) -> UserModel:
        user = await self.repo.get(id)
        if not user:
            logger.warning(f'User not found {id}')
            raise UserNotFoundError(user=id)
            
        logger.info(f'Найден пользователь: {user.username}')
        return user
    
    async def get_by_username(self, username: str) -> UserModel:
        user = await self.repo.get_by_username(username)
        if not user:
            logger.warning(f'User not found {username}')
            raise UserNotFoundError(user=username)
        logger.info(f'Найден пользователь: {user.username}')
        return user
    
    # async def get_multiple(self, ids: list):
    #     ids = [x.id for x in ids]
    #     users = await self.repo.get_multiple(ids)
    #     missed = []
    #     if not len(users) == len(ids):
    #         found = [x.id for x in users]
    #         missed = [x for x in ids if x not in found]
    #         logger.warning(f"Не найдены пользователи: {missed=}")
    #     else:
    #         logger.info(f"Найдены пользователи: {ids=}")
    #     return users, missed

    
    async def create(self, data: dict) -> UserModel:
        try:
            username = data['username']
            logger.info(f'Создаем пользователя: {username}')
            new_user = await self.repo.create(data)
            logger.info(f'Создан пользователь: {username}')

            event_data = UserData.model_validate(new_user)
            await self.producer.create(event_data)
            return new_user
        except IntegrityError as e:
            logger.error(f"Попытка повторно создать пользователя: {username}")
            raise UserAlreadyExistsError(user=username)
        
    async def update(self, data: UpdateUserDataDTO) -> UserModel:
        data_dict = asdict(data)
        user_id = data_dict.pop('id')
        user = await self.get_by_id(user_id)
        logger.info(f"Обновляем данные пользователя {user_id}")
        try:
            user = await self.repo.update(user, data_dict)
        except IntegrityError as e:
            logger.error(f"Попытка задать успользованное имя: {data.username}")
            raise UserAlreadyExistsError(user=data.username)
        logger.info(f"Данные пользователя {user_id} обновлены")

        event_data = UserData.model_validate(user)
        await self.producer.update(event_data)
        return user
    
    async def delete(self, user_id: int) -> str:
        await self.get_by_id(user_id)
        
        await self.repo.delete(user_id)
        logger.info(f"Удален пользователь {user_id=}")

        event_data=UserIdSchema(id=user_id)
        await self.producer.delete(event_data)
        return 'Successfully deleted'
