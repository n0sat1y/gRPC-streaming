import jwt
from typing import Annotated
from loguru import logger
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils import decode_jwt
from src.services.user import RpcUserService

bearer_scheme = HTTPBearer()
user_service = RpcUserService()

def get_token(creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
    try:
        token = creds.credentials
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

async def get_user(token_data = Depends(require_access_token)):
	user = await user_service.get_user_by_id(user_id=int(token_data['sub']))
	return user
