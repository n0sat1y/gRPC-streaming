from loguru import logger

from src.models.replications import ChatReplica


class ChatRepository:
    async def get(self, chat_id: int):
        try:
            return await ChatReplica.find_one(ChatReplica.chat_id == chat_id)
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e

    async def upsert_data(self, data: dict):
        try:
            chat_id = data.pop('id')
            print(data)
            chat = await ChatReplica.find_one(ChatReplica.chat_id == chat_id).upsert(
                {"$set": {
                    'members': data['members']
                }},
                on_insert=ChatReplica(chat_id=chat_id, members=data['members'])
            )
            return chat
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def delete(self, chat_id: int): 
        try:
            chat = await ChatReplica.find_one(ChatReplica.chat_id == chat_id).delete()
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
