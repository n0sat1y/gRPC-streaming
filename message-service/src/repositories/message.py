import asyncio
from typing import Optional

import pymongo
from beanie.operators import AddToSet, In, Pull, Set, Unset
from bson import ObjectId
from loguru import logger

from src.exceptions.message import MessageNotFoundError
from src.formatters.text_formatter import slim_text_formatter
from src.models import ForwardData, Message, MetaData, ReadProgress, ReplyData


class MessageRepository:
    async def get(self, message_id: str) -> Message | None:
        try:
            message = await Message.get(message_id)
            if not message:
                return None
            return message
        except Exception as e:
            logger.error(f"Database Error {e}")
            raise e

    async def get_context(
        self,
        chat_id: int,
        cursor_id: str | None,
        limit_before: int = 0,
        limit_after: int = 0,
    ):
        try:
            if not cursor_id:
                messages = (
                    await Message.find(Message.chat_id == chat_id)
                    .limit(limit_after + limit_before + 1)
                    .to_list()
                )
                return messages

            tasks = []
            center_oid = ObjectId(cursor_id)

            if limit_before > 0:
                query_before = (
                    Message.find(Message.chat_id == chat_id, Message.id < center_oid)
                    .sort(-Message.id)
                    .limit(limit_before)
                )
                tasks.append(query_before.to_list())

            if limit_after > 0:
                query_after = (
                    Message.find(Message.chat_id == chat_id, Message.id > center_oid)
                    .sort(Message.id)
                    .limit(limit_after)
                )
                tasks.append(query_after.to_list())

            results = await asyncio.gather(*tasks)

            messages_before = []
            messages_after = []

            task_index = 0
            if limit_before > 0:
                messages_before = results[task_index]
                messages_before.reverse()
                task_index += 1
            if limit_after > 0:
                messages_after = results[task_index]

            center_message = await Message.get(center_oid)

            return messages_before + [center_message] + messages_after
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def get_unread_count(
        self, chat_id: int, user_id: int, cursor_id: str | None = None
    ) -> int:
        try:
            request = [Message.chat_id == chat_id, Message.user_id != user_id]
            if cursor_id:
                request.append(Message.id > ObjectId(cursor_id))
            count = await Message.find(*request).count()
            return count
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def get_in_range(
        self, chat_id: int, first_message_id: str | None, last_message_id: str
    ) -> list[Message]:
        try:
            conditions = [Message.chat_id == chat_id]
            if first_message_id:
                conditions.append(Message.id >= ObjectId(first_message_id))
            conditions.append(Message.id <= ObjectId(last_message_id))
            messages = await Message.find_many(*conditions).to_list()
            return messages
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def insert(
        self,
        user_id: int,
        chat_id: int,
        content: str,
        reply_to: Optional[Message] = None,
    ) -> Message:
        try:
            metadata = MetaData()
            if reply_to:
                reply_data = ReplyData(
                    message_id=str(reply_to.id),
                    user_id=reply_to.user_id,
                    preview=(slim_text_formatter(reply_to.content)),
                )
                metadata.reply_to = reply_data
            message = Message(
                user_id=user_id, chat_id=chat_id, content=content, metadata=metadata
            )
            await message.insert()
            return message
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def delete(self, message: Message):
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def update(self, message: Message, new_content: str):
        try:
            update_data = {
                Message.content: new_content,
                Message.metadata.is_edited: True,
            }
            if message.metadata.reply_to:
                update_data[Message.metadata.reply_to.preview] = (
                    new_content if len(new_content) <= 50 else new_content[:47] + "..."
                )
            message = await message.update(Set(update_data))
            return message
        except Exception as e:
            logger.error(f"Database Error", e)
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
            logger.error(f"Database Error", e)
            raise e

    async def add_reaction(self, message_id: str, reaction: str, author: int) -> bool:
        try:
            result = await Message.find_one(Message.id == ObjectId(message_id)).update(
                AddToSet({Message.metadata.reactions[reaction]: author})
            )
            if result.matched_count == 0:
                raise MessageNotFoundError(message_id)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def remove_reaction(
        self, message_id: str, reaction: str, author: int
    ) -> bool:
        try:
            result = await Message.find_one(Message.id == ObjectId(message_id)).update(
                Pull({Message.metadata.reactions[reaction]: author})
            )
            if result.matched_count == 0:
                raise MessageNotFoundError(message_id)
            if result.modified_count > 0:
                await Message.find_one(
                    Message.id == ObjectId(message_id),
                    {f"metadata.reactions.{reaction}": {"$size": 0}},
                ).update(Unset({f"metadata.reactions.{reaction}": ""}))
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def forward_messages(
        self,
        user_id: int,
        chat_id: int,
        messages_data: list[Message],
        content: str | None = None,
    ) -> list[Message]:
        try:
            messages = []
            for old_message in messages_data:
                message = Message(
                    chat_id=chat_id, user_id=user_id, content=old_message.content
                )
                forward_data = ForwardData(
                    from_chat_id=old_message.chat_id,
                    from_message_id=str(old_message.id),
                    sender_user_id=old_message.user_id,
                )
                message_metadata = MetaData(forward_from=forward_data)
                message.metadata = message_metadata
                messages.append(message)

            if content:
                messages.append(
                    Message(user_id=user_id, chat_id=chat_id, content=content)
                )
            result = await Message.insert_many(messages)
            response = await Message.find(In(Message.id, result.inserted_ids)).to_list()
            return response
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e
