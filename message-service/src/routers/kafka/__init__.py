from faststream.kafka import KafkaBroker
from src.core.config import settings
from src.routers.kafka.subscriber import router

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
broker.include_router(router)
