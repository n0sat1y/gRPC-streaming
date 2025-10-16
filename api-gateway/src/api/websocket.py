import asyncio
from fastapi import APIRouter, Query, WebSocket, Depends, WebSocketDisconnect
from loguru import logger
from pydantic import ValidationError, TypeAdapter

from src.services.connection import manager
from src.schemas.websocket import *
from src.dependencies import get_user_id_for_websocket
from src.services.websocket import WebsocketHandler

router = APIRouter(prefix='/ws', tags=['Websockets'])
websocket_manager = WebsocketHandler()

@router.websocket('')
async def connection(
    ws: WebSocket,
    user_id = Depends(get_user_id_for_websocket)
):
    await manager.connect(user_id, ws)
    try:
        while True:
            recieve_data = await ws.receive_json()
            try:
                message: IncomingMessage = TypeAdapter(IncomingMessage).validate_python(recieve_data)
            except ValidationError as e:
                await ws.send_json(ErrorResponse(
                    payload=ErrorPayload(
                        code='VALIDATION_ERROR',
                        details=str(e)
                    )
                ).model_dump())
            
            response_data = await websocket_manager.handle_incoming_message(user_id, message)
            if response_data:
                await ws.send_json(response_data)
    except WebSocketDisconnect:
        manager.disconnect(user_id, ws)
    