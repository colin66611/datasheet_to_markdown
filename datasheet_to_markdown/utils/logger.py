"""Logging configuration module"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = __name__, level: int = logging.INFO, verbose: bool = False) -> logging.Logger:
    """
    Configure and return logger

    Args:
        name: Logger name
        level: Log level
        verbose: Whether to enable verbose output

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter
    if verbose:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter("%(message)s")

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
