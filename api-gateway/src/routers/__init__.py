from fastapi import APIRouter

from src.core.config import settings
from src.routers.user import router as user_router
from src.routers.chat import router as chat_router
from src.routers.messages import router as message_router

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(user_router)
router.include_router(chat_router)
router.include_router(message_router)
