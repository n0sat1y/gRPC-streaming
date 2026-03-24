import asyncio
import uuid
from collections import defaultdict
from typing import Optional, Tuple

import grpc
from bson import ObjectId
from faststream.kafka import KafkaBroker
from loguru import logger

from src.dto import ManyMessagesDTO, MessageDTO
from src.enums.grpc_enums import DirectionEnum
from src.exceptions.chat import *
from src.exceptions.message import *
from src.exceptions.user import *
from src.formatters.text_formatter import slim_text_formatter
from src.models import Message, MetaData, ReplyData
from src.models.replications import UserReplica
from src.repositories.message import MessageRepository
from src.repositories.read_progress import ReadProgressRepository
from src.routers.kafka.producer import KafkaPublisher
from src.schemas.message import *
from src.services.chat import ChatService
from src.services.policy import AccessPolicy
from src.services.user import UserService


class MessageService:
    def __init__(
        self,
        repo: MessageRepository,
        read_pregress_repo: ReadProgressRepository,
        user_service: UserService,
        chat_service: ChatService,
        kafka_producer: KafkaPublisher,
        access_policy: AccessPolicy,
    ):
        self.repo = repo
        self.progress_repo = read_pregress_repo
        self.user_service = user_service
        self.chat_service = chat_service
        self.kafka_producer = kafka_producer
        self.access_policy = access_policy

    async def get(self, message_id: str, get_full: bool = False) -> MessageDTO:
        logger.info(f"Получаем сообщение {message_id}")
        message = await self.repo.get(message_id)
        if not message:
            logger.warning(f"Не найдено сообщение {message_id}")
            raise MessageNotFoundError(message_id=message_id)
        message_data = MessageDTO(message=message)
        user_ids = set()
        user_ids.add(message.user_id)
        if message.metadata.reply_to:
            user_ids.add(message.metadata.reply_to.user_id)
        if message.metadata.forward_from:
            user_ids.add(message.metadata.forward_from.sender_user_id)

        if get_full:
            read_user_ids = await self.progress_repo.get_users_who_read_message(
                chat_id=message.chat_id, message_id=message_id
            )
            message_data.read_by = [id for id in read_user_ids if id != message.user_id]
            user_ids.update(set(read_user_ids))
        users = await self.user_service.get_multiple(list(user_ids))
        user_dict = {user.user_id: user for user in users}
        message_data.users = user_dict

        return message_data

    async def get_context(
        self,
        chat_id: int,
        user_id: int,
        direction: DirectionEnum,
        cursor_id: str | None = None,
        limit: int = 50,
    ) -> ManyMessagesDTO:
        chat = await self.chat_service.get(chat_id)
        user = await self.user_service.get(user_id)
        self.access_policy.can_see_chat(chat=chat, user_id=user_id)

        logger.info(
            f"Получаем сообщения из чата {chat_id=} ({direction=}, {cursor_id=})"
        )
        last_read_message = await self.progress_repo.get_last_read_message_by_user(
            chat_id=chat_id, user_id=user_id
        )
        unread_count_coro = self.repo.get_unread_count(
            chat_id=chat_id, user_id=user_id, cursor_id=last_read_message
        )
        limit -= 1

        if not cursor_id:
            cursor_id = last_read_message
        else:
            cursor_message = await self.repo.get(message_id=cursor_id)
            if not cursor_message or cursor_message.chat_id != chat_id:
                raise MessageNotFoundError(message_id=cursor_id)

        if direction == DirectionEnum.BEFORE:
            messages_coro = self.repo.get_context(
                chat_id=chat_id,
                cursor_id=cursor_id if cursor_id else None,
                limit_before=limit,
            )
        elif direction == DirectionEnum.AFTER:
            if not cursor_id:
                raise MessageNotFoundError(message_id=cursor_id)
            messages_coro = self.repo.get_context(
                chat_id=chat_id, cursor_id=cursor_id, limit_after=limit
            )
        else:
            limit_after = limit // 2
            limit_before = limit - limit_after
            if not cursor_id:
                raise MessageNotFoundError(message_id=cursor_id)
            messages_coro = self.repo.get_context(
                chat_id=chat_id,
                cursor_id=cursor_id,
                limit_before=limit_before,
                limit_after=limit_after,
            )

        messages, unread_count = await asyncio.gather(messages_coro, unread_count_coro)

        result = ManyMessagesDTO(
            messages=messages,
            last_read_message_id=last_read_message,
            unread_count=unread_count,
        )
        logger.info(f"Получено {len(result.messages)} сообщений из чата {chat_id=}")
        user_ids = set()
        for message in messages:
            user_ids.add(message.user_id)
            if message.metadata.reply_to:
                user_ids.add(message.metadata.reply_to.user_id)
            if message.metadata.forward_from:
                user_ids.add(message.metadata.forward_from.sender_user_id)
        users = await self.user_service.get_multiple(list(user_ids))
        user_dict = {user.user_id: user for user in users}
        result.users = user_dict
        return result

    async def insert(
        self,
        user_id: int,
        chat_id: int,
        content: str,
        request_id: str,
        sender_id: int,
        reply_to: Optional[str] = None,
    ) -> MessageDTO:
        chat = await self.chat_service.get(chat_id)
        user = await self.user_service.get(user_id)
        self.access_policy.can_see_chat(user_id, chat)

        metadata = MetaData()
        if reply_to:
            reply_to_message = (await self.get(reply_to)).message
            if reply_to_message.chat_id == chat_id:
                reply_to_user = await self.user_service.get(reply_to_message.user_id)
                reply_data = ReplyData(
                    message_id=reply_to,
                    user_id=reply_to_user.user_id,
                    preview=(slim_text_formatter(reply_to_message.content)),
                )
                metadata.reply_to = reply_data

        message = Message(
            user_id=user_id, chat_id=chat_id, content=content, metadata=metadata
        )
        message = await self.repo.insert(message)
        logger.info(f"Добавлено сообщение {message.id=} в {chat_id=}")

        await self.progress_repo.set_last_read_message(
            chat_id=chat_id, user_id=user_id, message_id=str(message.id)
        )
        logger.info(
            f"Счетчик последнего прочитанного сообщения обновлен ({user_id=}, {chat_id=}, {message.id=})"
        )

        users = await self.user_service.get_multiple(chat.members)
        active_recievers = [
            member.user_id for member in users if member.is_active == True
        ]

        event_data = MessageData(
            id=str(message.id),
            chat_id=message.chat_id,
            content=message.content,
            user_id=message.user_id,
            created_at=message.created_at,
        )
        await self.kafka_producer.create_message(
            recievers=active_recievers,
            data=event_data,
            request_id=request_id,
            sender_id=sender_id,
        )

        return MessageDTO(message=message)

    async def update(
        self, message_id: str, new_content: str, request_id: str, sender_id: int
    ) -> MessageDTO:
        logger.info(f"Обновляем сообщение {message_id}")

        message_data = await self.get(message_id)
        message = message_data.message
        self.access_policy.can_modify(user_id=sender_id, message=message)
        message = await self.repo.update(message, new_content)
        logger.info(f"Обновлено сообщение: {message_id}")

        active_recievers = await self.chat_service.get_active_members(
            chat_id=message.chat_id
        )
        event_data = UpdateMessagePayload(id=str(message.id), content=message.content)
        await self.kafka_producer.update_message(
            recievers=active_recievers,
            data=event_data,
            request_id=request_id,
            sender_id=sender_id,
        )
        logger.info(f"Уведомление об обновлении сообщения {message.id} отправлено")
        return MessageDTO(message=message)

    async def delete(self, message_id: str, request_id: str, sender_id: int) -> None:
        logger.info(f"Удаляем сообщение {message_id}")
        message = await self.get(message_id)
        self.access_policy.can_modify(sender_id, message.message)
        await self.repo.delete(message.message)
        logger.info(f"Удалено сообщение {message_id}")

        recievers = await self.chat_service.get_active_members(message.message.chat_id)
        await self.kafka_producer.delete_message(
            recievers=recievers,
            data=MessageIdPayload(id=str(message_id)),
            request_id=request_id,
            sender_id=sender_id,
        )

    async def delete_chat_messages(self, chat_id: int) -> None:
        logger.info(f"Удаляем сообщения чата {chat_id}")
        deleted_count = await self.repo.delete_chat_messages(chat_id)
        logger.info(f"Удалены {deleted_count} сообщения чата: {chat_id=}")

    async def mark_as_read(self, chat_id: int, user_id: int, message_id: str) -> None:
        user = await self.user_service.get(user_id)
        chat = await self.chat_service.get(chat_id)
        self.access_policy.can_see_chat(user_id=user_id, chat=chat)

        logger.info(f"Обновляем последнее прочитанное сообщение")
        previous_read_message = await self.progress_repo.get_last_read_message_by_user(
            chat_id=chat_id, user_id=user_id
        )
        await self.progress_repo.set_last_read_message(chat_id, user_id, message_id)
        logger.info(f"Последнее прочитанное сообщение пользователя {user_id} обновлено")
        read_messages_list = await self.repo.get_in_range(
            chat_id,
            previous_read_message if previous_read_message else None,
            message_id,
        )
        read_messages_list = read_messages_list[1:]
        authors = {}
        for message in read_messages_list:
            author_id = message.user_id
            if author_id != user_id:
                authors[author_id] = message
        if authors:
            last_read_chat_message = (
                await self.progress_repo.get_last_read_chat_message(
                    chat_id=chat_id, user_id=user_id
                )
            )
            event_data = []
            for author, message in authors.items():
                if message.id > ObjectId(last_read_chat_message):
                    event_data.append(
                        SlimMessageData(id=str(message.id), sender_id=author)
                    )
            await self.kafka_producer.read_message(data=event_data)

    async def add_reaction(self, message_id: str, reaction: str, author: int) -> None:
        await self.user_service.get(author)
        message = await self.get(message_id)
        logger.info(f"Добавляем реакцию в сообщение: {message_id}")
        result = await self.repo.add_reaction(message_id, reaction, author)
        if result > 0:
            recievers = await self.chat_service.get_active_members(
                message.message.chat_id
            )
            event_data = Reaction(message_id=message_id, reaction=reaction)
            await self.kafka_producer.add_reaction(
                data=event_data, sender_id=author, recievers=recievers
            )
        else:
            raise ReacionNotAdded()

    async def remove_reaction(
        self, message_id: str, reaction: str, author: int
    ) -> None:
        await self.user_service.get(author)
        message = await self.get(message_id)
        logger.info(f"Удаляем реакцию реакцию из сообщения: {message_id}")
        result = await self.repo.remove_reaction(message_id, reaction, author)
        if result > 0:
            recievers = await self.chat_service.get_active_members(
                message.message.chat_id
            )
            event_data = Reaction(message_id=message_id, reaction=reaction)
            await self.kafka_producer.remove_reaction(
                data=event_data, sender_id=author, recievers=recievers
            )
        else:
            raise ReacionNotAdded()

    async def forward_message(
        self,
        user_id: int,
        chat_id: int,
        messages: list[str],
        content: str | None,
        request_id: str,
    ):
        chat = await self.chat_service.get(chat_id)
        user = await self.user_service.get(user_id)
        self.access_policy.can_see_chat(user_id, chat)

        coros = []
        for message_id in messages:
            coros.append(self.get(message_id))

        messages_data = await asyncio.gather(*coros)
