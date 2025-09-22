import grpc
from fastapi import APIRouter

from protos import user_pb2_grpc, user_pb2

router = APIRouter(prefix='/user')

@router.get('/{user_id}')
async def get_user(id: int):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserStub(channel)
        request = user_pb2.GetUserByIdRequest(id=id)
        response = await stub.GetUserById(request)
        print(response.username)
        return response.username
