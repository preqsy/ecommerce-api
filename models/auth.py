from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from core.db import Base


class AuthUser(Base):
    __tablename__ = "auth_details"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(BigInteger, nullable=True, unique=True)
    password = Column(String, nullable=False)
    default_role = Column(String, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=True)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, nullable=False)
    auth_id = Column(
        ForeignKey(column="auth_details.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    phone_number = Column(BigInteger, nullable=False, unique=True)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, nullable=False)
    auth_id = Column(
        ForeignKey(column="auth_details.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    phone_number = Column(BigInteger, nullable=False, unique=True)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    ratings = Column(Integer, nullable=True)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
