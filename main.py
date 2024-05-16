from fastapi import FastAPI

from models import auth_user
from core.db import engine
from core.middleware import start_up_db
from endpoints import auth, customer

auth_user.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
def start_up():
    start_up_db()


app.include_router(auth.router)
app.include_router(customer.router)
