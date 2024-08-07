from datetime import datetime, timedelta
import threading

from fastapi import Depends
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer

from core import settings
from core.db import get_db
from core.errors import CredentialException, InvalidRequest
from crud import CRUDAuthUser, get_crud_auth_user, crud_refresh_token
from models.auth_user import AuthUser
from schemas.base import Roles
from .schema import Tokens, TokenData, RefreshTokenCreate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

BLACKLISTED_TOKEN = []

lock = threading.Lock()


async def deactivate_token(token, auth_id):
    if token in BLACKLISTED_TOKEN:
        raise InvalidRequest("Already Logged Out")
    verify_access_token(token)
    with lock:
        BLACKLISTED_TOKEN.append(token)
        await crud_refresh_token.delete_by_auth_id(auth_id=auth_id)


def is_token_blacklisted(token: str) -> bool:
    with lock:
        return token in BLACKLISTED_TOKEN


def encode_jwt(payload: dict, expiry_time: timedelta):
    data_to_encode = payload.copy()
    expiration_time = datetime.utcnow() + expiry_time
    data_to_encode.update({"exp": expiration_time})
    token = jwt.encode(data_to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return token


def generate_access_token(user_id, user_agent, default_role):
    payload = {
        "user_id": user_id,
        "type": "access",
        "user_agent": user_agent,
        "default_role": default_role,
    }
    access_token = encode_jwt(
        payload=payload,
        expiry_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_TIME),
    )
    return access_token


def generate_refresh_token(user_id, user_agent, default_role):
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "user_agent": user_agent,
        "default_role": default_role,
    }
    refresh_token = encode_jwt(
        payload=payload, expiry_time=timedelta(days=settings.REFRESH_TOKEN_EXPIRY_TIME)
    )
    return refresh_token


def generate_tokens(user_id, user_agent, default_role):
    access_token = generate_access_token(user_id, user_agent, default_role)
    refresh_token = generate_refresh_token(user_id, user_agent, default_role)
    return Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
        default_role=default_role,
    )


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
    except InvalidTokenError:
        raise CredentialException("Invalid token")
    return token_data


def get_current_auth_user(
    token=Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> AuthUser:
    # TODO: Change this to accept only verified emails when i deploy completely with background worker

    token = verify_access_token(token)
    auth_user = db.query(AuthUser).filter(AuthUser.id == token.user_id).first()
    if not auth_user:
        raise CredentialException("User not found")
    return auth_user


def get_current_unverified_auth_user(
    token=Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> AuthUser:
    token = verify_access_token(token)
    auth_user = db.query(AuthUser).filter(AuthUser.id == token.user_id).first()
    if not auth_user:
        raise CredentialException("User not found")

    return auth_user


def get_current_verified_vendor(
    token=Depends(oauth2_scheme),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
) -> AuthUser:
    # TODO: Change this to accept only verified emails and phone numbers  when i deploy completely with background worker
    token = verify_access_token(token)
    auth_user = crud_auth_user.get_or_raise_exception(id=token.user_id)
    if not (auth_user.default_role == Roles.VENDOR):
        raise InvalidRequest("Customer cannot perform this action")
    if not auth_user.role_id:
        raise InvalidRequest(
            "Complete your registration by creating your vendor account"
        )

    return auth_user


def get_current_verified_customer(
    token=Depends(oauth2_scheme),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
) -> AuthUser:
    # TODO: Change this to accept only verified emails and phone numbers  when i deploy completely with background worker

    token = verify_access_token(token)
    auth_user = crud_auth_user.get_or_raise_exception(id=token.user_id)

    if not (auth_user.default_role == Roles.CUSTOMER):
        raise InvalidRequest("Vendor cannot perform this action")

    if not auth_user.role_id:
        raise InvalidRequest(
            "Complete your registration by creating your customer account"
        )
    return auth_user


def create_forget_password_token(auth_id, user_agent):
    return encode_jwt(
        payload={"user_id": auth_id, "user_agent": user_agent},
        expiry_time=timedelta(minutes=settings.FORGET_PASSWORD_EXPIRY_TIME),
    )


async def regenerate_tokens(token, user_agent, auth_id, default_role):

    crud_refresh_token.check_if_refresh_token_exist(token)

    token = await deactivate_token(token, auth_id=auth_id)

    tokens = generate_tokens(
        user_agent=user_agent, user_id=auth_id, default_role=default_role
    )
    token_obj = RefreshTokenCreate(
        auth_id=auth_id, refresh_token=tokens.refresh_token, user_agent=user_agent
    )
    await crud_refresh_token.create(token_obj)
    return tokens
