from datetime import datetime
from unittest.mock import ANY
from models.auth_user import AuthUser
from schemas.otp import OTPType
from passlib.context import CryptContext
from utils.password_utils import pwd_context


def sample_auth_user_create():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "vendor",
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
        AuthUser.PASSWORD: pwd_context.hash("2Strong"),
        AuthUser.DEFAULT_ROLE: "customer",
        AuthUser.CREATED_TIMESTAMP: datetime.utcnow(),
        AuthUser.UPDATED_TIMESTAMP: None,
        AuthUser.PHONE_VERIFIED: True,
        AuthUser.EMAIL_VERIFIED: True,
        AuthUser.PHONE_NUMBER: None,
        AuthUser.ID: 1,
        AuthUser.ROLE_ID: None,
        AuthUser.IS_SUPERUSER: False,
        AuthUser.FIRST_NAME: "Obby",
        AuthUser.LAST_NAME: "Precious",
    }


def sample_auth_user_query_result_unverfied_email():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: pwd_context.hash("2Strong"),
        AuthUser.PHONE_VERIFIED: True,
        AuthUser.EMAIL_VERIFIED: False,
        AuthUser.ID: 1,
    }


def sample_auth_user_query_result_no_email():
    return {
        AuthUser.EMAIL: None,
        AuthUser.PASSWORD: pwd_context.hash("2Strong"),
        AuthUser.PHONE_VERIFIED: True,
        AuthUser.EMAIL_VERIFIED: True,
        AuthUser.ID: 1,
    }


def sample_auth_user_login_():
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


def sample_login_user_wrong_email():
    return {"username": "wrongemail.com", "password": "2Strong"}


def sample_header():
    return {"user-agent": "postman"}


def sample_access_token():

    return {"access_token": "banana"}
