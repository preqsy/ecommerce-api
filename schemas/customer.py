from schemas.base import CreateBaseModel, CustomerVendorReturnBase


class CustomerCreate(CreateBaseModel):
    """Customer Create"""


class CustomerReturn(CustomerVendorReturnBase):
    """Customer Return"""
