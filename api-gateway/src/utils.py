from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from src.core.config import settings


def hash_password(password: str):
	salt = bcrypt.gensalt()
	pwd = bcrypt.hashpw(password.encode(), salt)
	return pwd

def validate_password(user_password: str, model_password: bytes):
	return bcrypt.checkpw(user_password.encode(), model_password)

def encode_jwt(
		payload: dict, 
		type: str, 
		timedelta_minutes: int = 0, 
		timedelta_days: int = 0,
		key: str = settings.SECRET_KEY,
		algorithm: str = settings.JWT_ALGORITHM,
	):
	payload['iat'] = datetime.now(timezone.utc)
	payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=timedelta_minutes, days=timedelta_days)
	payload['type'] = type
	
	token = jwt.encode(payload, key, algorithm)
	return token

def encode_access_jwt(
		payload: dict, 
		token_lifetime_minutes: int = settings.JWT_ACCESS_LIFESPAN_MINUTES
	):
	return encode_jwt(payload, 'access', timedelta_minutes=token_lifetime_minutes)

def encode_refresh_jwt(
		payload: dict,
		token_lifetime_days: int = settings.JWT_REFRESH_LIFESPAN_DAYS
	):
	return encode_jwt(payload, 'refresh', timedelta_days=token_lifetime_days)

def decode_jwt(
		token: str,
		key: str = settings.SECRET_KEY,
		algorithm: str = settings.JWT_ALGORITHM
		) -> dict:
	data = jwt.decode(token, key, algorithms=[algorithm])
	return data
