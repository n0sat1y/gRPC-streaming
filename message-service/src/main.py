import asyncio
import grpc
from loguru import logger
from concurrent import futures
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from faststream import FastStream

from protos import message_pb2, message_pb2_grpc
from src.core.config import settings
from src.routers.grpc import Message as MessageRouter
from src.routers.kafka import broker
from src.models import Message as MessageModel, ReadProgress, ReadStatus, MetaData
from src.models.replications import UserReplica, ChatReplica

app = FastStream(broker)
server: grpc.aio.Server | None = None

@app.on_startup
async def startup():
    global server 
    motor_client = AsyncIOMotorClient(settings.MONGO_URL)
    await init_beanie(
        database=motor_client['messages'], 
        document_models=[
            MessageModel,
            UserReplica, 
            ChatReplica,
            ReadStatus,
            ReadProgress,
        ]
    )
    await MessageModel.find({"metadata": {"$exists": False}}).update_many(
        {"$set": {"metadata": MetaData().model_dump()}}
    )

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageRouter(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')

@app.on_shutdown
async def shutdown():
    await server.stop(1)

if __name__ == '__main__':
    asyncio.run(app.run())
