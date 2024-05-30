"Schemas"
from .auth import (
    AuthUserCreate,
    AuthUserResponse,
    AuthUserUpdate,
    VerifiedEmail,
    LogoutResponse,
    TokenDeactivate,
    RegisterAuthUserResponse,
)

from .customer import CustomerCreate, CustomerReturn

from .otp import OTPCreate, OTPType
from .product import (
    ProductCreate,
    ProductReturn,
    CartCreate,
    ProductUpdateReturn,
    ProductUpdate,
    CartReturn,
    CartUpdate,
    CartTotalAmount,
)
from .vendor import VendorCreate, VendorReturn
