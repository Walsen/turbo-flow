"""Structured logger for the Agent Adapter."""

from __future__ import annotations

import logging
import os
import sys

_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def get_logger(name: str = "tf-adapter") -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)

    level_str = os.environ.get("TF_ADAPTER_LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level_str, logging.INFO))

    return logger
