from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from app.core.config import settings


def setup_logger():
    """
    Устанавливает параметры логирования
    :return:
    """
    logger.remove()

    logger.add(
        settings.LOGS_DIR / "info.log",
        level="INFO",
        format=LOGURU_FORMAT,
        enqueue=True,
        backtrace=False,
        rotation="1 week",
        compression="zip",
        filter=lambda record: record["level"].no < logger.level("ERROR").no,
    )

    logger.add(
        settings.LOGS_DIR / "error.log",
        level="ERROR",
        format=LOGURU_FORMAT,
        enqueue=True,
        backtrace=True,
        rotation="1 week",
        compression="zip",
    )

    logger.add(
        settings.LOGS_DIR / "debug.log",
        level="DEBUG",
        format=LOGURU_FORMAT,
        enqueue=True,
        backtrace=True,
        rotation="1 week",
        compression="zip",
        filter=lambda record: record["level"].name == "DEBUG",
    )
