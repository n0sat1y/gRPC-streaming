from loguru import logger
from beanie.operators import Set, In, AddToSet, Pull
from bson import ObjectId

from src.models import Message, ReadProgress, ReadStatus
from src.exceptions.message import MessageNotFoundError

class MessageRepository:
    async def get(self, message_id: str, get_full: bool = False):
        try:
            message = await Message.get(message_id)
            if not message:
                return None
            if get_full:
                # await message.fetch_all_links()
                read_statuses = await ReadStatus.find(
                    ReadStatus.message_id.id == message.id
                ).to_list()
                message.read_by = read_statuses
            return message
        except Exception as e:
            logger.error(f'Database Error {e}')
            raise e

        
    async def get_all(self, chat_id: int, fetch_links: bool = False):
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
                Set(
                    {
                        Message.content: new_content,
                        Message.metadata.is_edited: True,
                    }
                )
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
            request_stmt.append(Message.user_id != read_by)
            messages = await Message.find(*request_stmt).to_list()

            if not messages:
                return []
            
            read_statuses = [
                ReadStatus(message_id=message.id, read_by=read_by)
                for message in messages
            ]
            if read_statuses:
                await ReadStatus.insert_many(read_statuses)

            unread_messages = [message for message in messages if not message.is_read]
            if not unread_messages:
                return []
            
            unread_ids = [msg.id for msg in unread_messages]
            await Message.find(
                In(Message.id, unread_ids)
            ).update(
                {"$set": {Message.is_read: True}}
            )
            for msg in unread_messages:
                msg.is_read = True

            return unread_messages
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

    async def add_reaction(self, message_id: str, reaction: str, author: str) -> bool:
        try:
            result = await Message.find_one(Message.id == ObjectId(message_id)).update(
                AddToSet({Message.metadata.reactions[reaction]: author})
            )
            if result.matched_count == 0:
                raise MessageNotFoundError(message_id)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e

    async def remove_reaction(self, message_id: str, reaction: str, author: str) -> bool:
        try:
            result = await Message.find_one(Message.id == ObjectId(message_id)).update(
                Pull({Message.metadata.reactions[reaction]: author})
            )
            if result.matched_count == 0:
                raise MessageNotFoundError(message_id)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Database Error', e)
            raise e
