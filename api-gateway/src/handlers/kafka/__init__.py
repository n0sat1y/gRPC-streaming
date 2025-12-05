from src.handlers.kafka.message import router as message_router
from src.handlers.kafka.presence import router as presence_router
from src.core.kafka import router

router.include_router(message_router)
router.include_router(presence_router)
