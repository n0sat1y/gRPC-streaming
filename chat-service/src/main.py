import asyncio
import grpc
from loguru import logger
from concurrent import futures

from protos import user_pb2_grpc
from src.core.config import settings



async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    ...

    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
