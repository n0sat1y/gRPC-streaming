import asyncio
import grpc
from fastapi import APIRouter, Query, WebSocket, Depends
from loguru import logger

from src.services.message import RpcMessageService 
from src.schemas.message import *
from src.dependencies import get_user

router = APIRouter(prefix='/message', tags=['Message'])
message_grpc_client = RpcMessageService()

@router.websocket('/ws')
async def message_flow(
    ws: WebSocket, 
    chat_id: int = Query(...),
    user_id = Depends(get_user)
):
    await ws.accept()

    client_task = asyncio.create_task(
        message_grpc_client.forward_websocket_message(user_id, chat_id, ws)
    )
    server_task = asyncio.create_task(
        message_grpc_client.wait_for_messages(chat_id, user_id, ws)
    )

    done, pending = await asyncio.wait(
        [client_task, server_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        logger.info("Отменяем незавершенную задачу...")
        task.cancel()

    try:
        await ws.close()
    except RuntimeError:
        pass
    
    logger.info(f"Соединение с user:{user_id} в чате:{chat_id} закрыто.")
    


@router.get('/{chat_id}')
async def get_all_messages(chat_id: int, user_id = Depends(get_user)):
    response = await RpcMessageService().get_all_messages(chat_id)
    return response




