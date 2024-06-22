from datetime import datetime
from typing import Any, Dict, List, Union
from fastapi import Depends

from core.db import get_db
from core.errors import InvalidRequest, MissingResources
from crud.base import CRUDBase
from models.cart import Cart
from schemas import CartCreate
from schemas.cart import CartUpdate


class CRUDCart(CRUDBase[Cart, CartCreate, CartUpdate]):
    def get_cart_items(self, customer_id) -> Union[List, None]:
        cart_details = (
            self._db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .all()
        )
        if not cart_details:
            return None
        return cart_details

    async def delete_cart(self, id) -> bool:
        cart_query = self._db.query(self.model).filter(self.model.customer_id == id)
        cart_query.delete(synchronize_session=False)
        self._db.commit()
        return

    async def delete_cart_item_by_product_id(self, product_id) -> bool:
        cart_query = self._db.query(self.model).filter(
            self.model.product_id == product_id
        )
        cart_query.delete(synchronize_session=False)
        self._db.commit()
        return

    async def get_cart_summary(
        self,
        customer_id: int,
    ):
        cart_items = self.get_cart_items(customer_id)
        if not cart_items:
            raise MissingResources("No items in cart")

        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        total_items_quantity = sum(item.quantity for item in cart_items)

        summary = {
            "total_items_quantity": total_items_quantity,
            "total_amount": total_amount,
            "cart_items": cart_items,
        }

        return summary

    def get_by_product_id(self, product_id: int) -> Cart:
        query_result = (
            self._db.query(self.model)
            .filter(self.model.product_id == product_id)
            .first()
        )
        if not query_result:
            return None
        return query_result

    def get_by_customer_id(self, customer_id: int) -> Cart:
        query_result = (
            self._db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .all()
        )
        if not query_result:
            return None
        return query_result

    async def update_cart_by_customer_id(
        self, customer_id, product_id, data_obj: CartUpdate
    ) -> Dict[str, Any]:
        query = (
            self._db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .filter(self.model.product_id == product_id)
        )

        data_dict = data_obj.model_dump(exclude_unset=True)
        data_dict["updated_timestamp"] = datetime.utcnow()
        query.update(data_dict, synchronize_session=False)
        self._db.commit()
        return data_dict

    async def check_if_product_id_exist_in_cart(self, customer_id, product_id):
        cart_item = self.get_by_customer_id(customer_id=customer_id)

        if not cart_item:
            raise InvalidRequest("No Cart Item")

        try:
            next(item for item in cart_item if item.product_id == product_id)
        except StopIteration:
            raise InvalidRequest("Id doesn't exist in cart")


def get_crud_cart(db=Depends(get_db)) -> CRUDCart:
    return CRUDCart(db=db, model=Cart)
