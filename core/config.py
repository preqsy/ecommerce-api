from pydantic_settings import BaseSettings
from pathlib import Path

path = Path.cwd()
env_path = path / ".env"


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    TEST_SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_TIME: int = 20
    REFRESH_TOKEN_EXPIRY_TIME: int = 30
    FORGET_PASSWORD_EXPIRY_TIME: int = 5
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str

    class Config:
        env_path = env_path
        env_file_encoding = "utf-8"


settings = Settings()
