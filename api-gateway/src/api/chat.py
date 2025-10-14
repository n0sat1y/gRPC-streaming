from fastapi import APIRouter, Depends

from src.services.grpc.chat import RpcChatService
from src.schemas.chat import *
from src.dependencies import get_user_id

router = APIRouter(prefix='/chat', tags=['Chat'])


@router.post('/')
async def create_chat(data: CreateChatRequest, user = Depends(get_user_id)) -> IdSchema:
    response = await RpcChatService().create_chat(data)
    return response

@router.get('/me')
async def get_chat_by_user_id(user_id = Depends(get_user_id)) -> MultipleChatsResponse:
    response = await RpcChatService().get_chats_by_user_id(user_id)
    return response

@router.get('/{chat_id}')
async def get_chat(chat_id: int, user = Depends(get_user_id)) -> ChatData:
    response = await RpcChatService().get_chat_by_id(chat_id)
    return response

@router.patch('/update')
async def update_chat(data: UpdateChatData, user = Depends(get_user_id)) -> IdSchema:
    response = await RpcChatService().update_chat(data)
    return response

@router.patch('/add-members')
async def update_chat(data: AddMembersRequest, user = Depends(get_user_id)) -> IdSchema:
    response = await RpcChatService().add_members(data)
    return response

@router.delete('/user-chat')
async def delete_user_from_chat(user_id: int, chat_id: int, auth_user = Depends(get_user_id)):
    response = await RpcChatService().delete_user_from_chat(user_id, chat_id)
    return response

@router.delete('/{chat_id}')
async def delete_chat(chat_id: int, user = Depends(get_user_id)):
    response = await RpcChatService().delete_chat(chat_id)
    return response

