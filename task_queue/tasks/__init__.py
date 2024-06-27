from .auth_user_tasks import *
from .cart_tasks import *
from .product_tasks import *


registered_tasks = [
    update_auth_password,
    update_auth_details,
    update_stock_after_checkout,
    save_product_images,
    add_shipping_details,
    add_order_items,
]
