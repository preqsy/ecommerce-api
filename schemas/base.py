"""Base Schema"""

from datetime import datetime
from enum import Enum
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints


class CreateBaseModel(BaseModel):

    first_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    last_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    username: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str


class ReturnBaseModel(BaseModel):
    id: int
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None


class RoleAuthDetailsUpdate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    role_id: int


class Roles(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"


class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME = "home"
    TOYS = "toys"
    BOOKS = "books"
    BEAUTY = "beauty"
    SPORTS = "sports"
    FOOD = "food"
    HEALTH = "health"
    AUTOMOTIVE = "automotive"
    PETS = "pets"
    SOFTWARE = "software"
    JEWELRY = "jewelry"
    BABY = "baby"
    GROCERY = "grocery"
    FURNITURE = "furniture"
    ART = "art"
    GAMES = "games"
