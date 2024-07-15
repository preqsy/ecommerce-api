from fastapi import FastAPI

from models import auth_user, order, product, cart, customer, vendor
from core.db import engine
from core.middleware import start_up_db
from api.endpoints import router

auth_user.Base.metadata.create_all(bind=engine)
product.Base.metadata.create_all(bind=engine)
cart.Base.metadata.create_all(bind=engine)
order.Base.metadata.create_all(bind=engine)
customer.Base.metadata.create_all(bind=engine)
vendor.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.on_event("startup")
def start_up():
    start_up_db()


app.include_router(router)
