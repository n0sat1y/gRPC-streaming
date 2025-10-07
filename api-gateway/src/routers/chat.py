from fastapi import APIRouter, Depends

from src.services.chat import RpcChatService
from src.schemas.chat import *
from src.dependencies import get_user

router = APIRouter(prefix='/chat', tags=['Chat'])


@router.post('/')
async def create_chat(data: CreateChatRequest, user_id = Depends(get_user)) -> ChatResponse:
    print(user_id)
    response = await RpcChatService().create_chat(data)
    return response

@router.get('/{chat_id}')
async def get_chat(chat_id: int, user_id = Depends(get_user)) -> ChatData:
    response = await RpcChatService().get_chat_by_id(chat_id)
    return response

@router.get('/me')
async def get_chat_by_user_id(user_id = Depends(get_user)) -> MultipleChatsResponse:
    response = await RpcChatService().get_chats_by_user_id(user_id)
    return response

@router.post('/add-members')
async def add_members(data: AddMembersToChatRequest, user_id = Depends(get_user)) -> ChatResponse:
    response = await RpcChatService().add_members_to_chat(data)
    return response

@router.delete('/user-chat')
async def delete_user_from_chat(user_id: int, chat_id: int, auth_user = Depends(get_user)):
    response = await RpcChatService().delete_user_from_chat(user_id, chat_id)
    return response

@router.delete('/{chat_id}')
async def delete_chat(chat_id: int, user_id = Depends(get_user)):
    response = await RpcChatService().delete_chat(chat_id)
    return response

