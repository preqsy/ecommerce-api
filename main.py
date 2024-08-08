from fastapi import FastAPI

from core.middleware import start_up_db
from api.endpoints import router


app = FastAPI()


@app.on_event("startup")
def start_up():
    start_up_db()


app.include_router(router)
