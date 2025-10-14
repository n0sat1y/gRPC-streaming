from fastapi import APIRouter

from src.core.config import settings
from src.api.user import router as user_router
from src.api.chat import router as chat_router
from src.api.messages import router as message_router
from src.api.auth import router as auth_router
from src.api.websocket import router as websocket_router

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(chat_router)
router.include_router(message_router)
router.include_router(websocket_router)
