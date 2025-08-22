"""Logging utilities that delegate to the Cortex logging system when available."""

import logging
from typing import Callable, Optional

cortex_setup_logging: Optional[Callable[..., None]]
get_logger: Optional[Callable[..., logging.Logger]]
try:
    from cortex.common.logging import setup_logging as cortex_setup_logging, get_logger
except ModuleNotFoundError:  # pragma: no cover - fallback when Cortex isn't installed
    cortex_setup_logging = None
    get_logger = None

_LOGGING_INITIALIZED = False


def _setup_cortex_logger(name: str) -> logging.Logger:
    global _LOGGING_INITIALIZED
    if not _LOGGING_INITIALIZED and cortex_setup_logging is not None:
        cortex_setup_logging()
        _LOGGING_INITIALIZED = True
    if get_logger is None:
        raise RuntimeError("Cortex logging is not available")
    return get_logger(name)


def setup_logging(name: str) -> logging.Logger:
    """Return a logger, using Cortex if it's available."""
    if cortex_setup_logging is not None and get_logger is not None:
        return _setup_cortex_logger(name)

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
