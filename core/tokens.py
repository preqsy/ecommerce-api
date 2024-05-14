from datetime import datetime, timedelta
from fastapi import Depends
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from core import settings
from core.errors import CredentialException
from .schema import Token, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


def verify_access_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.ALGORITHM)
        user_id = payload.get("user_id")
        if not user_id:
            CredentialException("invalid token")
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise CredentialException("Expired token")
    return token_data


def get_current_auth_user(token=Depends(oauth2_scheme)):
    token = verify_access_token(token)
