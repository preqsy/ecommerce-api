from datetime import datetime
from models.auth_user import AuthUser
from utils.password_utils import pwd_context


def sample_get_verified_vendor():
    return {
        AuthUser.EMAIL: "obbyprecious10@gmail.com",
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


def sample_customer_create():
    return {
        "first_name": "Enzo",
        "last_name": "Fernandez",
        "username": "preqsy",
        "phone_number": "+2347032937596",
        "auth_id": None,
        "country": "Nigeria",
        "state": "Lagos",
        "address": "Alimosho",
    }


def sample_vendor_create():
    return {
        "first_name": "Cristiano",
        "last_name": "Ronaldo",
        "username": "CR7",
        "phone_number": "+2347032937596",
        "auth_id": None,
        "country": "Portugal",
        "state": "Madeira",
        "address": "Alimosho",
        "bio": "Cool Vendor",
        "ratings": 4,
    }


def sample_product_create():
    return {
        "product_name": "Ps5",
        "product_image": "http://www.sample.org/head",
        "category": "fashion",
        "short_description": "Cool Game",
        "product_status": True,
        "long_description": "Nice Wrist Watch",
        "stock": 2,
        "price": 300,
    }


def sample_product_create_second():
    return {
        "product_name": "Macbook",
        "product_image": "http://www.sample.org/head",
        "category": "pets",
        "short_description": "Cool Game",
        "product_status": True,
        "long_description": "Nice Wrist Watch",
        "stock": 2,
        "price": 200,
    }


def sample_product_create_third():
    return {
        "product_name": "Iphone",
        "product_image": "http://www.sample.org/head",
        "category": "home",
        "short_description": "Cool Game",
        "product_status": True,
        "long_description": "Nice Wrist Watch",
        "stock": 2,
        "price": 500,
    }


def sample_product_update():
    return {
        "product_name": "On God",
        # "product_image": "http://www.sample.org/head",
        "category": "fashion",
        # "short_description": "Cool Game",
        # "long_description": "Nice Wrist Watch",
        "stock": 2,
        "price": 300,
    }
