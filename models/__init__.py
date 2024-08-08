from .auth_user import *
from .product import *
from .cart import *
from .order import *
from .customer import *
from .vendor import *

from core.db import engine

# auth_user.Base.metadata.create_all(bind=engine)
# product.Base.metadata.create_all(bind=engine)
# cart.Base.metadata.create_all(bind=engine)
# order.Base.metadata.create_all(bind=engine)
# customer.Base.metadata.create_all(bind=engine)
# vendor.Base.metadata.create_all(bind=engine)
