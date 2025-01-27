from fastapi import APIRouter

from .customer import router as customer_router
from .vendor import router as vendor_router
from .auth import router as auth_router
from .product import router as product_router
from .cart import router as cart_router
from .order import router as order_router
from .monitoring import router as monitoring_router


router = APIRouter()


router.include_router(auth_router)
router.include_router(customer_router)
router.include_router(vendor_router)
router.include_router(product_router)
router.include_router(order_router)
router.include_router(cart_router)
router.include_router(monitoring_router)
