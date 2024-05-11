import logging
import time

import psycopg2

from core import settings
from core.errors import DatabaseConnectionError

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(" %(levelname)s - %(name)s - %(asctime)s -  %(message)s")
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("application.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Add console handler to logger
logger.addHandler(console_handler)


def start_up_db():
    retries = 0
    max_retries = 3
    retry_delay = 5
    while retries < max_retries:
        try:
            conn = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URL)
            logger.info("Database Connection Successfull")
            return
        except Exception as error:
            retries += 1
            logger.error(
                f"Database connection failed (Attempts: {retries}/{max_retries})"
            )
            logger.error("Error: %s", error)
            time.sleep(retry_delay)
    logger.error(
        "Failed to establish database connection after %d attempts", max_retries
    )
    raise DatabaseConnectionError
