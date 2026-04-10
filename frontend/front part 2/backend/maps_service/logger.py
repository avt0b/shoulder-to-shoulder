import sys
from typing import Any

from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>",
    level="INFO",
    colorize=True,
    serialize=True,
)


def get_logger(name: str = __name__) -> Any:
    return logger.bind(name=name)
