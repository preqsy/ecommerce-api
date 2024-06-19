from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings

from crud import (
    get_crud_customer,
    get_crud_otp,
    get_crud_cart,
    get_crud_order,
    get_crud_product,
    get_crud_vendor,
    get_crud_auth_user,
)
from task_queue.tasks import registered_tasks
from core.db import get_db


REDIS_SETTINGS = RedisSettings()


async def get_queue_connection():
    return await create_pool(REDIS_SETTINGS)


async def startup(ctx):
    db = get_db()
    ctx["session"] = AsyncClient()
    ctx["crud_auth_user"] = get_crud_auth_user(db)
    ctx["crud_otp"] = get_crud_otp(db)
    ctx["crud_product"] = get_crud_product(db)
    ctx["crud_customer"] = get_crud_customer(db)
    ctx["crud_vendor"] = get_crud_vendor(db)
    ctx["crud_cart"] = get_crud_cart(db)
    ctx["crud_order"] = get_crud_order(db)


async def shutdown(ctx):
    await ctx["session"].aclose()


class WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
    functions = registered_tasks
