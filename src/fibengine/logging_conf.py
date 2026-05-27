"""Strukturerad logging med loguru. Binder run-id + config-hash till varje rad."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

_CONFIGURED = False


def setup_logging(run_id: str, config_hash: str, log_file: Path | None = None):
    """Konfigurera loguru en gång. Returnerar en logger bunden till run-kontext."""
    global _CONFIGURED
    if not _CONFIGURED:
        logger.remove()
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
            "run={extra[run_id]} cfg={extra[config_hash]} | "
            "<cyan>{name}:{function}:{line}</cyan> - {message}"
        )
        logger.add(sys.stderr, format=fmt, level="INFO")
        if log_file is not None:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(log_file, format=fmt, level="DEBUG")
        _CONFIGURED = True
    return logger.bind(run_id=run_id, config_hash=config_hash)
