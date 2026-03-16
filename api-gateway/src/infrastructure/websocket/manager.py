import asyncio
import json
from collections import defaultdict
from typing import Optional

from fastapi import Depends, WebSocket
from loguru import logger
from redis.asyncio import Redis

from src.core.redis import redis
from src.infrastructure.grpc_clients.presence import RpcPresenceService


class ConnectionManager:
    def __init__(self, redis_client: Redis, presence_service: RpcPresenceService):
        self.active_connections = defaultdict(list)
        self.listener_task: dict[int, asyncio.Task] = {}
        self.redis_client = redis_client
        self.presence_service = presence_service

    def _get_notification_channel(self, user_id: int):
        return f"user_notifications:{user_id}"

    async def _redis_listener(self, user_id: int, pubsub):
        try:
            async for message in pubsub.listen():
                if message["type"] == "subscribe":
                    continue

                for ws in self.active_connections.get(user_id, []):
                    await ws.send_text(message["data"])
        except Exception as e:
            logger.error(f"Ошибка в Redis-слушателе для user_id={user_id}: {e}")

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            pubsub = self.redis_client.pubsub()
            channel_name = self._get_notification_channel(user_id)
            await pubsub.subscribe(channel_name)
            task = asyncio.create_task(self._redis_listener(user_id, pubsub))
            self.listener_task[user_id] = task
            await self.presence_service.set_online(user_id)
        else:
            await self.presence_service.refresh_online(user_id)
        self.active_connections[user_id].append(websocket)
        logger.info(f"Пользователь {user_id} подключился.")

    async def disconnect(self, user_id, websocket: WebSocket):
        if (
            user_id in self.active_connections
            and websocket in self.active_connections[user_id]
        ):
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                task = self.listener_task.pop(user_id, None)
                if task:
                    task.cancel()
                del self.active_connections[user_id]
                await self.presence_service.set_offline(user_id)
