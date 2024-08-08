from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core import settings

print(f"Test database URL: {settings.TEST_SQLALCHEMY_DATABASE_URL}")

engine = create_engine(url=settings.TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def mock_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
