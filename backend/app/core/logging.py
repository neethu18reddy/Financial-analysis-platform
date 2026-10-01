"""Structured logging configuration."""

import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures application-wide logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
        if settings.LOG_FORMAT != "json"
        else '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("financial_platform")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
