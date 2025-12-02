from faststream.kafka import KafkaBroker
from faststream.kafka.router import KafkaRouter

from src.core.config import settings

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
