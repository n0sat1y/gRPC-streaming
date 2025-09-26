import grpc
from google.protobuf.json_format import MessageToDict
from fastapi import APIRouter

from src.services.chat import RpcChatService
from src.schemas.chat import *

router = APIRouter(prefix='/chat', tags=['Chat'])


@router.post('/')
async def create_chat(data: CreateChatRequest) -> ChatResponse:
    response = await RpcChatService().create_chat(data)
    return response

@router.get('/{chat_id}')
async def get_chat(chat_id: int) -> ChatData:
    response = await RpcChatService().get_chat_by_id(chat_id)
    return response

@router.get('/user/{user_id}')
async def get_chat_by_user_id(user_id: int) -> MultipleChatsResponse:
    response = await RpcChatService().get_chats_by_user_id(user_id)
    return response

@router.post('/add-members')
async def add_members(data: AddMembersToChatRequest) -> ChatResponse:
    response = await RpcChatService().add_members_to_chat(data)
    return response


