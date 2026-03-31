import asyncio

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import TypeAdapter, ValidationError

from src.dependencies import (get_connection_manager, get_presence_service,
                              get_user_id_for_websocket, get_websocket_handler)
from src.infrastructure.grpc_clients.presence import RpcPresenceService
from src.infrastructure.websocket.handler import WebsocketHandler
from src.infrastructure.websocket.manager import ConnectionManager
from src.schemas.websocket.websocket import *
from src.utils.exceptions import GrpcError

router = APIRouter(prefix="/ws", tags=["Websockets"])

PING_INTERVAL = 30


@router.websocket("")
async def connection(
    ws: WebSocket,
    user_id=Depends(get_user_id_for_websocket),
    _presence_service: RpcPresenceService = Depends(get_presence_service),
    _websocket_manager: WebsocketHandler = Depends(get_websocket_handler),
    _connection_manager: ConnectionManager = Depends(get_connection_manager),
):
    await _connection_manager.connect(user_id, ws)

    try:
        while True:
            try:
                recieve_data = await asyncio.wait_for(
                    ws.receive_json(), timeout=PING_INTERVAL
                )
                try:
                    await _presence_service.refresh_online(user_id)
                except GrpcError as e:
                    logger.warning(f"Failed to refresh online status: {e.detail}")
                if recieve_data == {"type": "pong"}:
                    continue

                try:
                    message: IncomingMessage = TypeAdapter(
                        IncomingMessage
                    ).validate_python(recieve_data)
                    print(message)
                except ValidationError as e:
                    await ws.send_json(
                        ErrorResponse(
                            payload=ErrorPayload(
                                code="VALIDATION_ERROR", details=str(e)
                            )
                        ).model_dump()
                    )

                result = await _websocket_manager.handle_incoming_message(
                    user_id, message
                )
                if result:
                    await ws.send_json(result)

            except asyncio.TimeoutError:
                await ws.send_json({"type": "ping"})

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected.")
    finally:
        logger.info(f"Cleaning up for user {user_id}...")
        await _connection_manager.disconnect(user_id, ws)
        logger.info(f"Cleanup for user {user_id} complete.")
