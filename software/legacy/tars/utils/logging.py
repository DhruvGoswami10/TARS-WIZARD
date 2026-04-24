"""Structured logging for TARS — file + terminal output."""

import logging
from pathlib import Path

_logger = None


def setup(log_file="tars.log", level=logging.INFO):
    """Set up logging to both file and terminal."""
    global _logger
    _logger = logging.getLogger("tars")
    _logger.setLevel(level)

    # Don't add handlers twice
    if _logger.handlers:
        return _logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # File handler — logs everything for debugging
    log_path = Path(log_file)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


def get_logger(name=None):
    """Get a child logger for a specific module."""
    if _logger is None:
        setup()
    if name:
        return _logger.getChild(name)
    return _logger
