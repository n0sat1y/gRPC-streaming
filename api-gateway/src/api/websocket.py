import asyncio
from fastapi import APIRouter, Query, WebSocket, Depends, WebSocketDisconnect
from loguru import logger

from src.services.connection import manager
from src.schemas.message import *
from src.dependencies import get_user_id_for_websocket

router = APIRouter(prefix='/ws', tags=['Websockets'])\

@router.websocket('')
async def connection(
    ws: WebSocket,
    # user_id: int = Query(...)
    # user_id = Depends(get_user)
    user_id = Depends(get_user_id_for_websocket)
):
    await manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, ws)
    