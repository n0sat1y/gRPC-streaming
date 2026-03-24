import asyncio

import grpc
from fastapi import APIRouter, Depends, Query, WebSocket
from loguru import logger

from src.dependencies import (get_chat_service, get_rpc_message_service,
                              get_user_id)
from src.infrastructure.grpc_clients.chat import RpcChatService
from src.infrastructure.grpc_clients.message import RpcMessageService
from src.schemas.api.message import GetAllMessagesResponse
from src.utils.enums.grpc_enums import DirectionEnum

router = APIRouter(prefix="/message", tags=["Message"])


@router.get("/all/{chat_id}")
async def get_all_messages(
    chat_id: int,
    cursor_id: str | None = None,
    direction: DirectionEnum = Query(DirectionEnum.UNSPECIFIED),
    limit: int = 10,
    user_id=Depends(get_user_id),
    _message_service: RpcMessageService = Depends(get_rpc_message_service),
    _chat_service: RpcChatService = Depends(get_chat_service),
):
    messages = await _message_service.get_context(
        chat_id=chat_id,
        user_id=user_id,
        cursor_id=cursor_id,
        direction=direction,
        limit=limit,
    )

    # return GetAllMessagesResponse(
    #     count=len(messages.messages),
    #     last_read_message_id=last_read_message if last_read_message else None,
    #     unread_count=unread_count,
    #     messages=messages.messages,
    #     user_data=messages.user_data,
    # )
    # print(messages)
    return messages


@router.get("/{message_id}")
async def get_message_data(
    message_id: str,
    _message_service: RpcMessageService = Depends(get_rpc_message_service),
):
    message = await _message_service.get_message_data(message_id)
    return message
