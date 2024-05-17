from typing import Optional

from schemas.base import CreateBaseModel, ReturnBaseModel


class CustomerCreate(CreateBaseModel):
    """Customer Create"""


class CustomerReturn(ReturnBaseModel):

    first_name: str
    last_name: str
    username: str
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str
    is_superuser: Optional[bool] = None
