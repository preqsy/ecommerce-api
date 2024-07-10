from datetime import datetime

from typing import Dict, List, Optional
from fastapi import Depends

from core.db import get_db
from core.errors import InvalidRequest, MissingResources
from crud.base import CRUDBase
from models import Cart, Product
from schemas import CartCreate, CartUpdate


class CRUDCart(CRUDBase[Cart, CartCreate, CartUpdate]):

    async def clear_cart(self, id):
        cart_query = self._db.query(self.model).filter(self.model.customer_id == id)
        cart_query.delete(synchronize_session=False)
        self._db.commit()

    async def delete_cart_item_by_product_id(self, product_id):
        cart_query = self._db.query(self.model).filter(
            self.model.product_id == product_id
        )
        cart_query.delete(synchronize_session=False)
        self._db.commit()

    async def get_cart_summary(
        self,
        customer_id: int,
    ) -> Dict:
        cart_items = self.get_cart_items_by_customer_id(customer_id)
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

    def get_by_product_id(self, product_id: int, customer_id: int) -> Optional[Cart]:

        query_result = (
            self._db.query(self.model)
            .filter(self.model.product_id == product_id)
            .filter(self.model.customer_id == customer_id)
            .first()
        )

        return query_result if query_result else None

    def get_cart_items_by_customer_id(self, customer_id: int) -> Optional[List[Cart]]:
        query_result = (
            self._db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .all()
        )
        return query_result if query_result else None

    async def update_cart_by_customer_id(
        self, customer_id: int, product_id: int, data_obj: CartUpdate
    ) -> Dict:
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

    async def check_if_product_id_exist_in_cart(
        self, customer_id, product_id
    ) -> List[Product]:
        cart_item = self.get_cart_items_by_customer_id(customer_id=customer_id)

        if not cart_item:
            raise InvalidRequest("No Cart Item")

        try:
            # Filter the cart items to get a list of products that match the given product ID
            product_list = [
                item.product for item in cart_item if item.product_id == product_id
            ]
            # Create an iterator for the filtered products list
            product_iter = iter(product_list)
            # Advance the iterator to the first item to check if there is at least one matching product
            next(product_iter)
            # If the product is found, return the list of matching products
            return product_list[0]

        except StopIteration:
            raise InvalidRequest("Product doesn't exist in cart")


def get_crud_cart(db=Depends(get_db)) -> CRUDCart:
    return CRUDCart(db=db, model=Cart)
