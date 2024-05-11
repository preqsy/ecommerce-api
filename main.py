from fastapi import FastAPI

from models import auth
from core.db import engine
from core.middleware import start_up_db

auth.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
def start_up():
    start_up_db()
