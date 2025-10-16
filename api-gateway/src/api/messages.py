import asyncio
import grpc
from fastapi import APIRouter, Query, WebSocket, Depends
from loguru import logger

from src.handlers.grpc.message import RpcMessageService
from src.dependencies import get_user_id

router = APIRouter(prefix='/message', tags=['Message'])
message_grpc_client = RpcMessageService()


@router.get('/all/{chat_id}')
async def get_all_messages(chat_id: int, user_id = Depends(get_user_id)):
    response = await message_grpc_client.get_all_messages(chat_id)
    return response

@router.post('/{chat_id}')
async def send_message(chat_id: int, content: str, user_id = Depends(get_user_id)):
    response = await message_grpc_client.send_message(user_id, chat_id, content)
    return response


