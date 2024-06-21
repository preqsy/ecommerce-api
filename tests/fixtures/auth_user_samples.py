from datetime import datetime


from models.auth_user import AuthUser
from schemas.otp import OTPType
from utils.password_utils import pwd_context


def sample_auth_user_create_customer():
    return {
        AuthUser.EMAIL: "obbyprecious12@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
    }


def sample_auth_user_create_vendor():
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
        AuthUser.DEFAULT_ROLE: "vendor",
        AuthUser.CREATED_TIMESTAMP: datetime.utcnow(),
        AuthUser.UPDATED_TIMESTAMP: None,
        AuthUser.PHONE_VERIFIED: True,
        AuthUser.EMAIL_VERIFIED: True,
        AuthUser.PHONE_NUMBER: None,
        AuthUser.ID: 1,
        AuthUser.ROLE_ID: 1,
        AuthUser.IS_SUPERUSER: False,
        AuthUser.FIRST_NAME: None,
        AuthUser.LAST_NAME: None,
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
    return {
        "user-agent": "PostmanRuntime/7.28.0",
        "host": "127.0.0.1",
    }
