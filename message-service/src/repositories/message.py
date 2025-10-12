from loguru import logger

from src.models import Message

class MessageRepository:
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
        
    async def delete_user_messages(self, user_id: int):
        try:
            messages = Message.find(Message.user_id == user_id)
            count = await messages.count()
            await messages.delete()
            return count
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
