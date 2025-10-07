from fastapi import APIRouter, Depends

from src.services import AuthService
from src.schemas.auth import TokenResponse
from src.dependencies import require_refresh_token

router = APIRouter(prefix='/auth', tags=['Auth'])
service = AuthService()

@router.post('/login')
async def login(username: str, password: str) -> TokenResponse:
    response = await service.login(username, password)
    return response

@router.post('/register')
async def register(username: str, password: str) -> dict:
    response = await service.register(username, password)
    return {'id': response}

@router.get('/refresh')
async def refresh(payload = Depends(require_refresh_token)) -> TokenResponse:
    response = await service.refresh(payload)
    return response
