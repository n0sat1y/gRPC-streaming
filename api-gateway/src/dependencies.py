from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from src.features.auth.service import AuthService
from src.infrastructure.grpc_clients import grpc_service
from src.infrastructure.grpc_clients.chat import RpcChatService
from src.infrastructure.grpc_clients.message import RpcMessageService
from src.infrastructure.grpc_clients.presence import RpcPresenceService
from src.infrastructure.grpc_clients.user import RpcUserService
from src.infrastructure.websocket.handler import WebsocketHandler
from src.utils.utils import decode_jwt

bearer_scheme = HTTPBearer()


def decode_token(token: str):
    try:
        return decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    except jwt.PyJWTError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token(creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
    token = creds.credentials
    return decode_token(token)


def require_refresh_token(payload=Depends(get_token)) -> dict:
    if payload["type"] == "refresh":
        return payload
    logger.warning("Передан неверный тип токена")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
    )


def require_access_token(payload=Depends(get_token)) -> dict:
    if payload["type"] == "access":
        return payload
    logger.warning("Передан неверный тип токена")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
    )


def get_user_id(token_data=Depends(require_access_token)):
    return int(token_data["sub"])


def get_user_id_for_websocket(token: str = Query(...)):
    payload = decode_token(token)
    if not payload["type"] == "access":
        logger.warning("Передан неверный тип токена")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )
    return int(payload["sub"])


def get_chat_stub():
    return grpc_service.chat


def get_message_stub():
    return grpc_service.message


def get_presence_stub():
    return grpc_service.presence


def get_user_stub():
    return grpc_service.user


def get_chat_service(stub=Depends(get_chat_stub)):
    return RpcChatService(stub)


def get_message_service(stub=Depends(get_message_stub)):
    return RpcMessageService(stub)


def get_presence_service(stub=Depends(get_presence_stub)):
    return RpcPresenceService(stub)


def get_user_service(stub=Depends(get_user_stub)):
    return RpcUserService(stub)


def get_auth_service(service=Depends(get_user_service)):
    return AuthService(service)


def get_websocket_handler(message_service=Depends(get_message_service)):
    return WebsocketHandler(message_service)
