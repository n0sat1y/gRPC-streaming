from loguru import logger
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        logger.info(f"Пользователь {user_id} подключился.")

    def disconnect(self, user_id, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
        logger.info(f"Пользователь {user_id} отключился.")

    async def send_personal_message(self, user_id: int, data: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                await ws.send_json(data)
            logger.info(f"Отправлено сообщение пользователю {user_id}")

    async def broadcast(self, recievers: list[int], data: dict):
        for reciever in recievers:
            for ws in self.active_connections[reciever]:
                await ws.send_json(data)
                logger.info(f"Отправлено сообщение пользователю {reciever}")
                print(self.active_connections)

manager = ConnectionManager()
