import asyncio
import grpc
from loguru import logger
from concurrent import futures
from faststream import FastStream

from protos import presence_pb2, presence_pb2_grpc
from src.core.config import settings
from src.routers.grpc import Presence
from src.routers.kafka import broker
from src.services.ttl_listener import TtlListener

app = FastStream(broker)
server: grpc.aio.Server | None = None
ttl_listener_task: asyncio.Task | None = None

@app.on_startup
async def startup():
    global server, ttl_listener_task
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    presence_pb2_grpc.add_PresenceServicer_to_server(Presence(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    await server.start()
    logger.info(f'Listening on port :{settings.GRPC_PORT}')

    ttl_listener = TtlListener(broker)
    ttl_listener_task = asyncio.create_task(ttl_listener.listen())
    logger.info("Фоновая задача для прослушивания истечения срока действия ключа Redis запущена")


@app.on_shutdown
async def shutdown():
    if ttl_listener_task:
        ttl_listener_task.cancel()
        try:
            await ttl_listener_task
        except asyncio.CancelledError:
            logger.info("Задача прослушивателя TTL успешно отменена")
    
    if server:
        await server.stop(1)
    
    logger.info("Сервис остановлен")

if __name__ == '__main__':
    asyncio.run(app.run())

