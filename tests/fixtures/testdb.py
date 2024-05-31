from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core import settings
from httpx import AsyncClient

from main import app
import pytest

from models import auth_user, product, cart as cartmodel


engine = create_engine(url=f"{settings.SQLALCHEMY_DATABASE_URL}_test")
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def mock_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
# @pytest.fixture(scope="module")
def client():
    # Drop Tables
    auth_user.Base.metadata.drop_all(bind=engine)
    product.Base.metadata.drop_all(bind=engine)
    cartmodel.Base.metadata.drop_all(bind=engine)
    # Creat tables
    auth_user.Base.metadata.create_all(bind=engine)
    product.Base.metadata.create_all(bind=engine)
    cartmodel.Base.metadata.create_all(bind=engine)
    client = AsyncClient(app=app, base_url="https://127.0.0.1/")
    yield client
