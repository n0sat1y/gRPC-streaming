from faststream.kafka.fastapi import KafkaRouter
from src.core.config import settings

router = KafkaRouter(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
