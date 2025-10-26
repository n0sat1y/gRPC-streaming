from faststream.kafka.fastapi import KafkaRouter
from src.handlers.kafka.message import router as message_router
from src.handlers.kafka.presence import router as presence_router

router = KafkaRouter()
router.include_router(message_router)
router.include_router(presence_router)
