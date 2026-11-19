"""Small newline-safe application logger."""

import logging
import re

logger = logging.getLogger("jagaawan")
if not logger.handlers:
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)


def safe(message: object) -> str:
    return re.sub(r"[\r\n\t]", " ", str(message))


def info(message: object) -> None:
    logger.info(safe(message))


def warning(message: object) -> None:
    logger.warning(safe(message))


def error(message: object) -> None:
    logger.error(safe(message))
