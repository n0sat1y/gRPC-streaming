from fastapi import APIRouter, Depends

from src.handlers.grpc.chat import RpcChatService
from src.schemas.chat import *
from src.dependencies import get_user_id, get_chat_service

router = APIRouter(prefix='/chat', tags=['Chat'])

@router.get('/me')
async def get_chat_by_user_id(user_id = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> MultipleChatsResponse:
    response = await _service.get_chats_by_user_id(user_id)
    return response

@router.get('/{chat_id}')
async def get_group(chat_id: int, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> ChatData:
    response = await _service.get_chat_by_id(chat_id, user)
    return response

@router.post('/group/')
async def create_group_chat(data: CreateGroupChatRequest, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> IdSchema:
    response = await _service.create_group_chat(data)
    return response

@router.post('/private/')
async def get_or_create_private(target_id: int, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> IdSchema:
    response = await _service.get_or_create_private_chat(
        GetOrCreatePrivateChatRequest(current_user_id=user, target_user_id=target_id)
    )
    return response

@router.patch('/update')
async def update_chat(data: UpdateChatData, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> IdSchema:
    response = await _service.update_chat(data)
    return response

@router.patch('/add-members')
async def add_members(data: AddMembersRequest, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)) -> IdSchema:
    response = await _service.add_members(data)
    return response

@router.delete('/user-chat')
async def delete_user_from_chat(user_id: int, chat_id: int, auth_user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)):
    response = await _service.delete_user_from_chat(user_id, chat_id)
    return response

@router.delete('/{chat_id}')
async def delete_chat(chat_id: int, user = Depends(get_user_id), _service: RpcChatService = Depends(get_chat_service)):
    response = await _service.delete_chat(chat_id)
    return response

