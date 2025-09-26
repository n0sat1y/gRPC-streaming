import grpc
from loguru import logger

from src.core.config import settings
from protos import user_pb2_grpc, user_pb2

class RpcService:
    def __init__(self):
        self.user_connection_url = f"{settings.GRPC_HOST}:{settings.GRPC_USER_PORT}"

    async def get_user_by_id(self, user_id: int):
        try:
            async with grpc.aio.insecure_channel(self.user_connection_url) as channel:
                stub = user_pb2_grpc.UserStub(channel)
                request = user_pb2.GetUserByIdRequest(id=user_id)
                response = await stub.GetUserById(request)
            logger.info(f'Получен пользователь: {response.username}')
            return response.username
        except Exception as e:
            logger.error(f'Ошибка при получении пользователя {user_id=}', e)
