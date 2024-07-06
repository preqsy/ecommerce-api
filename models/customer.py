from __future__ import annotations

from sqlalchemy import (
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
    phone_number = Column(String, nullable=True, unique=True)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
    cart_items = relationship("Cart", back_populates="customer")
