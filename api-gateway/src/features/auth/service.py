from fastapi import HTTPException
from loguru import logger

from src.infrastructure.grpc_clients.user import RpcUserService
from src.schemas.api.auth import TokenResponse
from src.utils.utils import (decode_jwt, encode_access_jwt, encode_refresh_jwt,
                             hash_password, validate_password)


class AuthService:
    def __init__(self, user_service: RpcUserService):
        self.rpc_service = user_service

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.rpc_service.get_user_with_password(username)
        if validate_password(password, user.password):
            access = encode_access_jwt({"sub": str(user.user_id)})
            refresh = encode_refresh_jwt({"sub": str(user.user_id)})
            return TokenResponse(access_token=access, refresh_token=refresh)
        raise HTTPException(status_code=400, detail="Wrong password")

    async def register(self, username: str, password: str) -> int:
        password = hash_password(password)
        user_id = await self.rpc_service.create_user(username, password)
        return user_id

    async def refresh(self, payload: dict) -> TokenResponse:
        user_id = payload.get("sub")
        access = encode_access_jwt({"sub": user_id})
        return TokenResponse(access_token=access)
