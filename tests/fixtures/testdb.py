from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core import settings


engine = create_engine(url=f"{settings.SQLALCHEMY_DATABASE_URL}_test")
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def mock_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
