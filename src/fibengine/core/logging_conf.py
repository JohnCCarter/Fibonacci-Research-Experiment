"""Strukturerad logging med loguru. Binder run-id + config-hash till varje rad."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

_STDERR_CONFIGURED = False
_FILE_SINKS: dict[Path, int] = {}


def setup_logging(run_id: str, config_hash: str, log_file: Path | None = None):
    """Konfigurera loguru sinks och returnera en logger bunden till run-kontext."""
    global _STDERR_CONFIGURED
    if not _STDERR_CONFIGURED:
        logger.remove()
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
            "run={extra[run_id]} cfg={extra[config_hash]} | "
            "<cyan>{name}:{function}:{line}</cyan> - {message}"
        )
        logger.add(sys.stderr, format=fmt, level="INFO")
        _STDERR_CONFIGURED = True
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
            "run={extra[run_id]} cfg={extra[config_hash]} | "
            "<cyan>{name}:{function}:{line}</cyan> - {message}"
        )

    if log_file is not None:
        log_file = log_file.resolve()
        if log_file not in _FILE_SINKS:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            _FILE_SINKS[log_file] = logger.add(log_file, format=fmt, level="DEBUG")
    return logger.bind(run_id=run_id, config_hash=config_hash)
