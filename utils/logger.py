import logging
import re

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("jagaawan")


def _sanitize(msg: str) -> str:
    return re.sub(r"[\r\n\t]", " ", str(msg))


def info(msg: str) -> None:
    logger.info(_sanitize(msg))


def warning(msg: str) -> None:
    logger.warning(_sanitize(msg))


def error(msg: str) -> None:
    logger.error(_sanitize(msg))
