import grpc
from fastapi import APIRouter, Depends

from src.handlers.grpc.user import RpcUserService
from src.dependencies import get_user_id
from src.schemas.user import UpdateUserDataSchema

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/{user_id}/')
async def get_user(id: int, _reciever_id = Depends(get_user_id)):
    response = await RpcUserService().get_user_by_id(id)
    return response

@router.patch('/')
async def get_user(data: UpdateUserDataSchema, _reciever_id = Depends(get_user_id)):
    response = await RpcUserService().update_user(_reciever_id, data)
    return response

@router.delete('/{user_id}/')
async def delete_user(id: int, _reciever_id = Depends(get_user_id)):
    response = await RpcUserService().delete_user(id)
    return {'status': response}
