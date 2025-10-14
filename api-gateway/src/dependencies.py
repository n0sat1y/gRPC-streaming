import jwt
from typing import Annotated
from loguru import logger
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils import decode_jwt

bearer_scheme = HTTPBearer()

def decode_token(token: str):
    try:
        return decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Not authenticated')
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
	

def require_refresh_token(payload = Depends(get_token)) -> dict:
	if payload['type'] == 'refresh':
		return payload
	logger.warning('Передан неверный тип токена')
	raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')

def require_access_token(payload = Depends(get_token)) -> dict:
	print(payload)
	if payload['type'] == 'access':
		return payload
	logger.warning('Передан неверный тип токена')
	raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')

def get_user_id(token_data = Depends(require_access_token)):
	return int(token_data['sub'])

def get_user_id_for_websocket(token: str = Query(...)):
    payload = decode_token(token)
    if not payload['type'] == 'access':
        logger.warning('Передан неверный тип токена')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')
    return int(payload['sub'])
