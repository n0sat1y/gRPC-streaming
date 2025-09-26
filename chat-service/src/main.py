import asyncio
import grpc
from loguru import logger
from concurrent import futures

from protos import chat_pb2, chat_pb2_grpc
from src.core.config import settings
from src.routers import Chat



async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)

    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
