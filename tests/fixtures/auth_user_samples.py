from datetime import datetime
from unittest.mock import ANY
from models.auth_user import AuthUser
from schemas.otp import OTPType


def sample_auth_user_create():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
    }


def sample_auth_user_wrong_email():
    return {
        AuthUser.EMAIL: "obbyprecious12.@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
    }


def sample_auth_user_invalid_password():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: "we",
        AuthUser.DEFAULT_ROLE: "customer",
    }


def sample_auth_user_query_result_first():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
        AuthUser.CREATED_TIMESTAMP: datetime.utcnow(),
        AuthUser.UPDATED_TIMESTAMP: None,
        AuthUser.PHONE_VERIFIED: False,
        AuthUser.EMAIL_VERIFIED: False,
        AuthUser.PHONE_NUMBER: None,
        AuthUser.ID: ANY,
        AuthUser.ROLE_ID: None,
        AuthUser.IS_SUPERUSER: False,
        AuthUser.FIRST_NAME: None,
        AuthUser.LAST_NAME: None,
    }


def sample_auth_user_login():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        # AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
        AuthUser.CREATED_TIMESTAMP: datetime.utcnow(),
        AuthUser.UPDATED_TIMESTAMP: None,
        AuthUser.PHONE_VERIFIED: True,
        AuthUser.EMAIL_VERIFIED: True,
        AuthUser.PHONE_NUMBER: None,
        AuthUser.ID: ANY,
        AuthUser.ROLE_ID: ANY,
        AuthUser.IS_SUPERUSER: False,
        AuthUser.FIRST_NAME: "Obinna",
        AuthUser.LAST_NAME: "Obinna",
    }


def sample_verify_auth_user():
    return {
        "auth_id": "1",
        "token": "930287",
        "otp_type": OTPType.EMAIL,
    }


def sample_login_user():
    return {"username": "obbyprecious12@gmail.com", "password": "2Strong"}


def sample_header():
    return {"user-agent": "postman"}
