"""
Structured logging with episode/step context.
"""

from __future__ import annotations

import logging
import sys
from typing import Any


_LOG_FORMAT = "[%(levelname)s] %(name)s | %(message)s"


def get_logger(name: str = "athleteos") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class EpisodeLogger:
    """Convenience wrapper that injects episode/step context into log messages."""

    def __init__(self, logger: logging.Logger | None = None):
        self._log = logger or get_logger()
        self._episode_id: str = ""
        self._step: int = 0

    def set_context(self, episode_id: str, step: int = 0) -> None:
        self._episode_id = episode_id
        self._step = step

    def _prefix(self) -> str:
        if self._episode_id:
            return f"[ep={self._episode_id[:8]} step={self._step}] "
        return ""

    def info(self, msg: str, **kw: Any) -> None:
        self._log.info(f"{self._prefix()}{msg}", **kw)

    def warning(self, msg: str, **kw: Any) -> None:
        self._log.warning(f"{self._prefix()}{msg}", **kw)

    def error(self, msg: str, **kw: Any) -> None:
        self._log.error(f"{self._prefix()}{msg}", **kw)

    def debug(self, msg: str, **kw: Any) -> None:
        self._log.debug(f"{self._prefix()}{msg}", **kw)
