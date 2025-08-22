"""Logging utilities that delegate to the Cortex logging system when available."""

import logging

try:
    from cortex.common.logging import setup_logging as cortex_setup_logging, get_logger
except ModuleNotFoundError:  # pragma: no cover - fallback when Cortex isn't installed
    cortex_setup_logging = None
    get_logger = None

_LOGGING_INITIALIZED = False


def _setup_cortex_logger(name: str) -> logging.Logger:
    global _LOGGING_INITIALIZED
    if not _LOGGING_INITIALIZED:
        cortex_setup_logging()
        _LOGGING_INITIALIZED = True
    return get_logger(name)


def setup_logging(name: str) -> logging.Logger:
    """Return a logger, using Cortex if it's available."""
    if cortex_setup_logging and get_logger:
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
