from faststream.kafka import KafkaBroker

from src.core.config import settings

broker = KafkaBroker(f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}")
