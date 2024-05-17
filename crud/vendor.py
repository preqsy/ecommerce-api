from fastapi import Depends
from core.db import get_db
from crud.base import CRUDBase
from models.auth_user import Vendor
from schemas.vendor import VendorCreate


class CRUDVendor(CRUDBase[Vendor, VendorCreate, VendorCreate]):
    pass


def get_crud_vendor(db=Depends(get_db)):
    return CRUDVendor(db=db, model=Vendor)
