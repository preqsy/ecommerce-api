from pydantic_settings import BaseSettings
from pathlib import Path

path = Path.cwd()
env_path = path / ".env"


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = (
        "postgresql://postgres:50610903@localhost:5432/e-commerce"
    )
    JWT_SECRET_KEY: str = "09qnjal2u32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY_TIME: int = 20
    REFRESH_TOKEN_EXPIRY_TIME: int = 30

    class Config:
        env_path = env_path
        env_file_encoding = "utf-8"


settings = Settings()
