from typing import Any
from pydantic import AnyHttpUrl, RedisDsn
from pydantic_settings import BaseSettings
from pathlib import Path

path = Path.cwd()
env_path = path / ".env"


class PaystackConfig(BaseSettings):
    BASE_URL: str = "https://api.paystack.co/"
    SECRET_KEY: str = ""
    CALLBACK_URL: str = "https://127.0.0.0.1:8000/cart/checkout"

    class Config:
        case_sensitve = True
        env_prefix = "PAYSTACK_"
        env_path = env_path
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = ""
    TEST_SQLALCHEMY_DATABASE_URL: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    JWT_SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRY_TIME: int = 20
    REFRESH_TOKEN_EXPIRY_TIME: int = 30
    FORGET_PASSWORD_EXPIRY_TIME: int = 5
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    MAIL_SECRET_KEY: str = ""
    SWIFTBUY_MAIL: str = "swiftbuyx@gmail.com"
    MAIL_PORT: int
    SMTP_SERVER: str = "smtp.gmail.com"
    paystack_config: PaystackConfig = PaystackConfig()

    class Config:
        env_path = env_path
        env_file_encoding = "utf-8"


settings = Settings()
