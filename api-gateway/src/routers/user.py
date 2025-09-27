import grpc
from fastapi import APIRouter

from src.services.user import RpcUserService

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/{user_id}')
async def get_user(id: int):
    response = await RpcUserService().get_user_by_id(id)
    return {'username': response}

@router.post('/')
async def create_user(username: str):
    response = await RpcUserService().create_user(username)
    return {'id': response}
