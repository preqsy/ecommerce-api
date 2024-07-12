from arq import cron
from arq.cron import CronJob

from .order import check_order_items_and_update_order_status_to_shipped


def at_every_x_minutes(x: int, start: int = 0, end: int = 59):
    return {*list(range(start, end, x))}


def get_cron_jobs():
    return [_update_order_status()]


def _update_order_status() -> CronJob:
    return cron(
        check_order_items_and_update_order_status_to_shipped,  # type:ignore
        minute=at_every_x_minutes(10),
        unique=True,
        run_at_startup=True,
    )
