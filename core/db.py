from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from core import settings


print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URL}")
engine = create_engine(url=settings.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
