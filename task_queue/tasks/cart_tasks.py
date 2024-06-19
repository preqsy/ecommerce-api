from typing import List
from crud import CRUDProduct
from models import Product


async def update_stock_after_checkout(ctx, product_ids: List, new_stock: int):
    crud_product: CRUDProduct = ctx["crud_product"]

    for index, ids in enumerate(product_ids):
        crud_product.get_or_raise_exception(ids)
        await crud_product.update(id=ids, data_obj={Product.STOCK: new_stock[index]})
