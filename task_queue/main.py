from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings

from crud.otp import get_crud_otp
from task_queue.tasks import registered_tasks
from core.db import get_db
from crud.auth import get_crud_auth_user


REDIS_SETTINGS = RedisSettings()


async def get_queue_connection():
    return await create_pool(REDIS_SETTINGS)


async def startup(ctx):
    db = get_db()
    ctx["session"] = AsyncClient()
    ctx["crud_auth_user"] = get_crud_auth_user(db)
    ctx["crud_otp"] = get_crud_otp(db)


async def shutdown(ctx):
    await ctx["session"].aclose()


class WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
    functions = registered_tasks
