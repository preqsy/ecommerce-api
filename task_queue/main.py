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
    get_crud_order_item,
    get_crud_payment_details,
    get_crud_shipping_details,
    get_crud_product_image,
)
from task_queue.cron_jobs.main import get_cron_jobs
from task_queue.tasks import registered_tasks
from core.db import get_db
from core import settings


REDIS_SETTINGS = RedisSettings(host=settings.REDIS_HOST)


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
    ctx["crud_product_image"] = get_crud_product_image(db)
    ctx["crud_shipping_details"] = get_crud_shipping_details(db)
    ctx["crud_payment_details"] = get_crud_payment_details(db)
    ctx["crud_order_item"] = get_crud_order_item(db)


async def shutdown(ctx):
    await ctx["session"].aclose()


class WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
    functions = registered_tasks
    cron_jobs = get_cron_jobs()
