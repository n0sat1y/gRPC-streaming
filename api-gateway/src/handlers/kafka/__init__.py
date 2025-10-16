from faststream.kafka.fastapi import KafkaRouter
from src.handlers.kafka.message import router as message_router

router = KafkaRouter()
router.include_router(message_router)
