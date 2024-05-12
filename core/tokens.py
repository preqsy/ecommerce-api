from datetime import datetime, timedelta
from jose import jwt, JWTError

from core import settings
from .schema import Token


def encode_jwt(payload: dict, expiry_time: timedelta):
    data_to_encode = payload.copy()
    expiration_time = datetime.utcnow() + expiry_time
    data_to_encode.update({"exp": expiration_time})
    token = jwt.encode(data_to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return token


def generate_access_token(user_id):
    payload = {"user_id": user_id, "type": "access"}
    access_token = encode_jwt(
        payload=payload,
        expiry_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_TIME),
    )
    return access_token


def generate_refresh_token(user_id):
    payload = {"user_id": user_id, "type": "refresh"}
    refresh_token = encode_jwt(
        payload=payload, expiry_time=timedelta(days=settings.REFRESH_TOKEN_EXPIRY_TIME)
    )
    return refresh_token


def generate_tokens(user_id):
    access_token = generate_access_token(user_id)
    refresh_token = generate_refresh_token(user_id)
    return Token(access_token=access_token, refresh_token=refresh_token)
