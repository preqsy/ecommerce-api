from pydantic_settings import BaseSettings
from pathlib import Path

path = Path.cwd()
env_path = path / ".env"


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str

    class Config:
        env_path = env_path
        env_file_encoding = "utf-8"


settings = Settings()
