from loguru import logger
from fastapi import WebSocket
from collections import defaultdict

from src.handlers.grpc.presence import RpcPresenceService

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)
        self.presence_service = RpcPresenceService()
        
        

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            await self.presence_service.set_online(user_id)
        else:
            await self.presence_service.refresh_online(user_id)
        self.active_connections[user_id].append(websocket)
        logger.info(f"Пользователь {user_id} подключился.")

    async def disconnect(self, user_id, websocket: WebSocket):
        if user_id in self.cleaning_in_progress:
            return

        if user_id in self.active_connections and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                await self.kill(user_id, set_offline=True)

    async def kill(self, user_id: int, set_offline: bool = True):
        if user_id in self.cleaning_in_progress:
            return 

        if user_id not in self.active_connections:
            if set_offline:
                await self.presence_service.set_offline(user_id)
            return

        try:
            self.cleaning_in_progress.add(user_id)

            connections_to_close = self.active_connections.pop(user_id, [])
            for connection in connections_to_close:
                await connection.close()
            
            if set_offline:
                await self.presence_service.set_offline(user_id)
        finally:
            self.cleaning_in_progress.remove(user_id)

    async def send_personal_message(self, user_id: int, data: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                await ws.send_json(data)
            logger.info(f"Отправлено сообщение пользователю {user_id}")

    async def broadcast(self, recievers: list[int], data: dict):
        for reciever in recievers:
            await self.send_personal_message(reciever, data)

manager = ConnectionManager()
