import asyncio
import grpc
from loguru import logger
from concurrent import futures
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from protos import message_pb2, message_pb2_grpc
from src.core.config import settings
from src.routers import Message as MessageRouter
from src.models import Message as MessageModel



async def serve():
    motor_client = AsyncIOMotorClient(settings.MONGO_URL)
    await init_beanie(
        database=motor_client['messages'], 
        document_models=[
            MessageModel,
        ]
    )

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageRouter(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
