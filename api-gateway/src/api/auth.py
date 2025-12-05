from fastapi import APIRouter, Depends

from src.services.auth import AuthService
from src.schemas.auth import TokenResponse
from src.dependencies import require_refresh_token, get_auth_service


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/login')
async def login(username: str, password: str, _service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    response = await _service.login(username, password)
    return response

@router.post('/register')
async def register(username: str, password: str, _service: AuthService = Depends(get_auth_service)) -> dict:
    response = await _service.register(username, password)
    return {'id': response}

@router.get('/refresh')
async def refresh(payload = Depends(require_refresh_token), _service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    response = await _service.refresh(payload)
    return response
