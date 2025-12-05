import grpc
from fastapi import APIRouter, Depends

from src.handlers.grpc.user import RpcUserService
from src.dependencies import get_user_id, get_user_service
from src.schemas.user import UpdateUserDataSchema

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/{user_id}/')
async def get_user(
    id: int, 
    _reciever_id = Depends(get_user_id), 
    _service: RpcUserService = Depends(get_user_service)
):
    response = await _service.get_user_by_id(id)
    return response

@router.patch('/')
async def get_user(
    data: UpdateUserDataSchema, 
    _reciever_id = Depends(get_user_id), 
    _service: RpcUserService = Depends(get_user_service)
):
    response = await _service.update_user(_reciever_id, data)
    return response

@router.delete('/{user_id}/')
async def delete_user(
    id: int, 
    _reciever_id = Depends(get_user_id), 
    _service: RpcUserService = Depends(get_user_service)
):
    response = await _service.delete_user(id)
    return {'status': response}
