"""Logging configuration."""

import logging
import sys
from typing import Optional


def setup_logging(
    name: Optional[str] = None, level: int = logging.INFO
) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
