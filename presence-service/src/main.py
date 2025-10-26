import asyncio
import grpc
from loguru import logger
from concurrent import futures
from faststream import FastStream

from protos import presence_pb2, presence_pb2_grpc
from src.core.config import settings
from src.routers.grpc import Presence
from src.routers.kafka import broker

app = FastStream(broker)
server: grpc.aio.Server | None = None

@app.on_startup
async def startup():
    global server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    presence_pb2_grpc.add_PresenceServicer_to_server(Presence(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')

@app.on_shutdown
async def shutdown():
    await server.stop(1)

if __name__ == '__main__':
    asyncio.run(app.run())

