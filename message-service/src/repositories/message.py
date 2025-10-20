from loguru import logger
from beanie.operators import Set

from src.models import Message, ReadProgress, ReadStatus

class MessageRepository:
    async def get(self, message_id: str):
        try:
            message = await Message.get(message_id)
            return message
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def get_all(self, chat_id: int):
        try:
            messages = await Message.find_many(Message.chat_id == chat_id).to_list()
            return messages
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def insert(self, message: Message):
        try:
            await message.insert()
            return message
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def delete(self, message: Message):
        try:
            await message.delete()
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def update(self, message: Message, new_content: str):
        try:
            message = await message.update(
                Set({Message.content: new_content})
            )
            return message
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    # async def delete_user_messages(self, user_id: int):
    #     try:
    #         messages = Message.find(Message.user_id == user_id)
    #         count = await messages.count()
    #         await messages.delete()
    #         return count
    #     except Exception as e:
    #         logger.error(f'Database Error', e)
    #         raise e
    
    async def delete_chat_messages(self, chat_id: int):
        try:
            messages = Message.find(Message.chat_id == chat_id)
            count = await messages.count()
            await messages.delete()
            return count
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e

    async def mark_as_read(last_message_id: str):
        try:
            pass
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def set_last_read_message(self, chat_id: int, user_id: int) -> str | None:
        try:
            message_id = await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id,
                ReadProgress.user_id == user_id
            )
            return message_id.last_read_message_id
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def set_last_read_message(self, chat_id: int, user_id: int, message_id: int) -> None:
        try:
            await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id,
                ReadProgress.user_id == user_id
            ).upsert(
                Set({ReadProgress.last_read_message_id: message_id}),
                on_insert=ReadProgress(user_id=user_id, chat_id=chat_id, last_read_message_id=message_id)
            )
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
