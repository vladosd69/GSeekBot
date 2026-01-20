import logging
import coloredlogs
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)


def configure_logging(file_name: str) -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    coloredlogs.install(
        level="DEBUG",
        logger=root_logger,
        fmt=log_format,
        datefmt=date_format,
    )

    file_handler = RotatingFileHandler(
        f"logs/{file_name}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(file_handler)

    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("aiogram").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
