from fastapi import APIRouter

from src.core.config import settings
from src.routers.user import router as user_router

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(user_router)
