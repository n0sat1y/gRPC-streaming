import asyncio
import grpc
from fastapi import APIRouter, Query, WebSocket, Depends
from loguru import logger

from src.handlers.grpc.message import RpcMessageService
from src.handlers.grpc.chat import RpcChatService
from src.dependencies import get_user_id, get_chat_service, get_message_service
from src.schemas.message import GetAllMessagesResponse

router = APIRouter(prefix='/message', tags=['Message'])


@router.get('/all/{chat_id}')
async def get_all_messages(
    chat_id: int, 
    user_id = Depends(get_user_id), 
    _message_service: RpcMessageService = Depends(get_message_service),
    _chat_service: RpcChatService = Depends(get_chat_service),
):
    messages = await _message_service.get_all_messages(chat_id)
    # last_read_message = await _chat_service.get_last_read_message(chat_id, user_id)
    # unread_count = 0
    # for message in messages.messages:
    #     if message.id > last_read_message: unread_count += 1

    # return GetAllMessagesResponse(
    #     count=len(messages.messages),
    #     last_read_message_id=last_read_message if last_read_message else None,
    #     unread_count=unread_count,
    #     messages=messages.messages
    # )
    print(messages)
    return messages


@router.get('/{message_id}')
async def get_message_data(message_id: str, _message_service: RpcMessageService = Depends(get_message_service)):
    message = await _message_service.get_message_data(message_id)
    return message
