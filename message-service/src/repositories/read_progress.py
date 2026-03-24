from beanie.operators import Set
from bson import ObjectId
from loguru import logger

from src.models import Message, ReadProgress


class ReadProgressRepository:
    async def get_last_read_chat_message(
        self, chat_id: int, user_id: int
    ) -> str | None:
        try:
            progress = (
                await ReadProgress.find(
                    ReadProgress.chat_id == chat_id,
                    ReadProgress.user_id != user_id,
                    sort=[("_id", -1)],
                )
                .limit(1)
                .to_list()
            )
            return (
                str(progress[0].last_read_message_id.ref.id)
                if progress and progress[0].last_read_message_id
                else None
            )

        except Exception as e:
            logger.error(f"Database Error: {e}")
            raise e

    async def get_last_read_message_by_user(
        self, chat_id: int, user_id: int
    ) -> str | None:
        try:
            progress = await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id,
                ReadProgress.user_id == user_id,
            )
            return (
                str(progress.last_read_message_id.ref.id)
                if progress and progress.last_read_message_id
                else None
            )
        except Exception as e:
            logger.error(f"Database Error: {e}")
            raise e

    async def get_users_who_read_message(
        self, chat_id: int, message_id: str
    ) -> list[int]:
        try:
            cursors = await ReadProgress.find(
                ReadProgress.chat_id == chat_id,
                ReadProgress.last_read_message_id >= ObjectId(message_id),
            ).to_list()
            return [cursor.user_id for cursor in cursors]

        except Exception as e:
            logger.error(f"Database Error", e)
            raise e

    async def set_last_read_message(
        self, chat_id: int, user_id: int, message_id: str
    ) -> None:
        try:
            message_obj = await Message.get(ObjectId(message_id))
            if not message_obj:
                raise ValueError(f"Message with id {message_id} not found")

            await ReadProgress.find_one(
                ReadProgress.chat_id == chat_id, ReadProgress.user_id == user_id
            ).upsert(
                Set({ReadProgress.last_read_message_id: message_obj.id}),
                on_insert=ReadProgress(
                    user_id=user_id,
                    chat_id=chat_id,
                    last_read_message_id=message_obj.id,
                ),
            )
        except Exception as e:
            logger.error(f"Database Error", e)
            raise e
