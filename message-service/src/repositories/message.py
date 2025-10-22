from loguru import logger
from beanie.operators import Set
from bson import ObjectId

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
        
    async def mark_as_read(
            self, 
            previous_message_read: str | None, 
            last_read_message: str,
            read_by: int
        ) -> list[Message]:
        try:
            request_stmt = [Message.id <= ObjectId(last_read_message)]
            if previous_message_read:
                request_stmt.append(Message.id > ObjectId(previous_message_read))

            messages = await Message.find(*request_stmt).to_list()
            changed_messages = []

            for message in messages:
                if not message.user_id == read_by:
                    await ReadStatus(message_id=message.id, read_by=read_by).insert()
                    if not message.is_read:
                        message.is_read = True
                        await message.save()
                        changed_messages.append(message)

            return changed_messages
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
        
    async def get_last_read_message(self, chat_id: int, user_id: int):
        try:
            progress = await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id,
                ReadProgress.user_id == user_id,
            )
            return str(progress.last_read_message_id.ref.id) if progress and progress.last_read_message_id else None
        except Exception as e:
            logger.error(f'Database Error: {e}')
            raise e
        
    async def set_last_read_message(self, chat_id: int, user_id: int, message_id: str) -> None:
        try:
            message_obj = await Message.get(ObjectId(message_id))
            if not message_obj:
                raise ValueError(f"Message with id {message_id} not found")
                
            await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id,
                ReadProgress.user_id == user_id
            ).upsert(
                Set({ReadProgress.last_read_message_id: message_obj.id}),
                on_insert=ReadProgress(
                    user_id=user_id, 
                    chat_id=chat_id, 
                    last_read_message_id=message_obj.id
                )
            )
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
