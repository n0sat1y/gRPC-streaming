import grpc
from loguru import logger
from faststream.kafka import KafkaBroker
from sqlalchemy.exc import IntegrityError

from src.repositories import UserRepository
from src.exceptions.user import (
    UserNotFoundError, UserAlreadyExistsError
)
from src.schemas.user import *

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    async def get_by_id(self, id: int):
        user = await self.repo.get(id)
        if not user:
            logger.warning(f'User not found {id}')
            raise UserNotFoundError(user=id)
            
        logger.info(f'Найден пользователь: {user.username}')
        return user
    
    async def get_by_username(self, username: str):
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

    
    async def create(self, data: dict, broker: KafkaBroker):
        try:
            username = data['username']
            logger.info(f'Создаем пользователя: {username}')
            new_user = await self.repo.create(data)
            logger.info(f'Создан пользователь: {username}')

            event_data = UserData.model_validate(new_user)
            await broker.publish(
                UserCreatedEvent(data=event_data), 'user.event')
            logger.info(f"Уведомление о создании пользователя {new_user.id} отправлено")

            return new_user
        except IntegrityError as e:
            logger.error(f"Попытка повторно создать пользователя: {username}")
            raise UserAlreadyExistsError(user=username)
    
    async def delete(self, user_id: int, broker: KafkaBroker):
        await self.get_by_id(user_id)
        
        await self.repo.delete(user_id)
        logger.info(f"Удален пользователь {user_id=}")

        await broker.publish(UserDeactivateEvent(data=UserIdSchema(id=user_id)), 'user.event')
        logger.info(f'Отправлено уведомление об удалении пользователя {user_id=}')

        return 'Successfully deleted'
