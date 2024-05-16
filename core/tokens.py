from datetime import datetime, timedelta
import threading
from fastapi import Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from core import settings
from core.db import get_db
from core.errors import CredentialException, InvalidRequest
from models.auth_user import AuthUser
from .schema import Tokens, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

BLACKLISTED_TOKEN = []

lock = threading.Lock()


def deactivate_token(token):
    with lock:
        BLACKLISTED_TOKEN.append(token)


def is_token_blacklisted(token: str) -> bool:
    with lock:
        return token in BLACKLISTED_TOKEN


def encode_jwt(payload: dict, expiry_time: timedelta):
    data_to_encode = payload.copy()
    expiration_time = datetime.utcnow() + expiry_time
    data_to_encode.update({"exp": expiration_time})
    token = jwt.encode(data_to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return token


def generate_access_token(user_id, user_agent):
    payload = {"user_id": user_id, "type": "access", "user_agent": user_agent}
    access_token = encode_jwt(
        payload=payload,
        expiry_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_TIME),
    )
    return access_token


def generate_refresh_token(user_id, user_agent):
    payload = {"user_id": user_id, "type": "refresh", "user_agent": user_agent}
    refresh_token = encode_jwt(
        payload=payload, expiry_time=timedelta(days=settings.REFRESH_TOKEN_EXPIRY_TIME)
    )
    return refresh_token


def generate_tokens(user_id, user_agent):
    access_token = generate_access_token(user_id, user_agent)
    refresh_token = generate_refresh_token(user_id, user_agent)
    return Tokens(access_token=access_token, refresh_token=refresh_token)


def verify_access_token(token):
    if is_token_blacklisted(token):
        raise InvalidRequest("User logged out")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.ALGORITHM)
        user_id = payload.get("user_id")
        user_agent = payload.get("user_agent")
        if not user_id:
            CredentialException("invalid token")
        token_data = TokenData(user_id=user_id, user_agent=user_agent)
    except JWTError:
        raise CredentialException("Expired token")
    return token_data


def get_current_auth_user(token=Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token = verify_access_token(token)
    auth_user = db.query(AuthUser).filter(AuthUser.id == token.user_id).first()
    if not auth_user or not auth_user.email_verified:
        raise CredentialException("User not found or emailt not verified")
    return auth_user
