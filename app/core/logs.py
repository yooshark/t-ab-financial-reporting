import logging
from typing import Final

from app.core.enums import LoggingLevel

DEFAULT_LOG_LEVEL: Final[LoggingLevel] = LoggingLevel.INFO

FMT: Final[str] = "[%(asctime)s] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
DATEFMT: Final[str] = "%Y-%m-%d %H:%M"


def configure_logging(
    *,
    level: LoggingLevel = DEFAULT_LOG_LEVEL,
) -> None:
    logging.basicConfig(
        level=level,
        datefmt=DATEFMT,
        format=FMT,
        force=True,
    )
