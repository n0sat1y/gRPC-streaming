import grpc
from fastapi import APIRouter, Depends

from src.services.user import RpcUserService
from src.dependencies import get_user_id

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/{user_id}')
async def get_user(id: int, _reciever_id = Depends(get_user_id)):
    response = await RpcUserService().get_user_by_id(id)
    return response

@router.delete('/{user_id}')
async def delete_user(id: int, _reciever_id = Depends(get_user_id)):
    response = await RpcUserService().delete_user(id)
    return {'status': response}
