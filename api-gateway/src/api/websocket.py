import asyncio
from fastapi import APIRouter, Query, WebSocket, Depends, WebSocketDisconnect
from loguru import logger
from pydantic import ValidationError, TypeAdapter

from src.services.connection import manager
from src.schemas.websocket import *
from src.dependencies import get_user_id_for_websocket
from src.services.websocket import WebsocketHandler
from src.handlers.grpc.presence import RpcPresenceService

router = APIRouter(prefix='/ws', tags=['Websockets'])
websocket_manager = WebsocketHandler()
presence_service = RpcPresenceService()

PING_INTERVAL = 40

@router.websocket('')
async def connection(
    ws: WebSocket,
    user_id = Depends(get_user_id_for_websocket)
):
    await manager.connect(user_id, ws)
    await presence_service.set_online(user_id)

    try:
        while True:
            try:
                recieve_data = await ws.receive_json()
                try:
                    message: IncomingMessage = TypeAdapter(IncomingMessage).validate_python(recieve_data)
                    print(message)
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

            except asyncio.TimeoutError:
                await presence_service.refresh_online(user_id)
                await ws.send_json({"type": "ping"})

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected.")
        await presence_service.set_offline(user_id)
        manager.disconnect(user_id, ws)
    # finally:
    #     logger.info(f"Cleaning up for user {user_id}...")
    #     await presence_service.set_offline(user_id)
    #     manager.disconnect(user_id, ws)
    #     logger.info(f"Cleanup for user {user_id} complete.")
    