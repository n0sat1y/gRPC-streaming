from loguru import logger

from src.models.replications import UserReplica


class UserRepository:
    async def upsert_data(self, data: dict):
        try:
            user_id = data.pop('id')
            user = await UserReplica.find_one(UserReplica.user_id == user_id).upsert(
                {"$set": {**data}},
                on_insert=UserReplica(user_id=user_id, **data)
            )
            return user
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def deactivate(self, user_id: int): 
        try:
            user = await UserReplica.find(UserReplica.user_id == user_id).update(
                {"$set": {'is_active': False}}
            )
            return user
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
