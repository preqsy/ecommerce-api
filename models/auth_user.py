from __future__ import annotations

from typing import ClassVar
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship
from core.db import Base


class AuthUser(Base):

    __tablename__ = "auth_details"
    ID: ClassVar[str] = "id"
    ROLE_ID: ClassVar[str] = "role_id"
    FIRST_NAME: ClassVar[str] = "first_name"
    LAST_NAME: ClassVar[str] = "last_name"
    EMAIL: ClassVar[str] = "email"
    PHONE_NUMBER: ClassVar[str] = "phone_number"
    EMAIL_VERIFIED: ClassVar[str] = "email_verified"
    PHONE_VERIFIED: ClassVar[str] = "phone_verified"
    PASSWORD: ClassVar[str] = "password"
    DEFAULT_ROLE: ClassVar[str] = "default_role"
    IS_SUPERUSER: ClassVar[str] = "is_superuser"
    CREATED_TIMESTAMP: ClassVar[str] = "created_timestamp"
    UPDATED_TIMESTAMP: ClassVar[str] = "updated_timestamp"

    id = Column(Integer, primary_key=True, nullable=False)
    role_id = Column(Integer, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    password = Column(String, nullable=False)
    default_role = Column(String, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, nullable=False)
    auth_id: Column[int] = Column(

        ForeignKey("auth_details.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    refresh_token = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    user_agent = Column(String, nullable=True)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    expires_on = Column(
        TIMESTAMP(timezone=True), server_default=text("now() + interval '14 days'")
    )


class OTP(Base):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True, nullable=False)
    auth_id: Column[int] = Column(
        ForeignKey(column="auth_details.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    otp = Column(String, nullable=False)
    otp_type = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    no_of_tries = Column(Integer)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    expires_on = Column(
        TIMESTAMP(timezone=True), server_default=text("now() + interval '14 days'")
    )
