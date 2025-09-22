import asyncio
import grpc
from loguru import logger
from concurrent import futures
from fast_depends import Depends

from protos import user_pb2, user_pb2_grpc
from src.core.config import settings
from src.routers import User
from src.services import UserService



async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(User(), server)

    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
