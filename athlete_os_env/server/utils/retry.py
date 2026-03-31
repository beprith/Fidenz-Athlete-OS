"""
Exponential backoff decorator for LLM / network calls.
"""

from __future__ import annotations

import asyncio
import functools
import time
from typing import Any, Callable, Type, Tuple

from server.utils.logger import get_logger

log = get_logger("retry")


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Synchronous exponential-backoff retry decorator."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_retries:
                        log.error(f"{fn.__name__} failed after {max_retries} attempts: {exc}")
                        raise
                    log.warning(f"{fn.__name__} attempt {attempt} failed: {exc}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            return None  # unreachable
        return wrapper
    return decorator


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Async exponential-backoff retry decorator."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_retries:
                        log.error(f"{fn.__name__} failed after {max_retries} attempts: {exc}")
                        raise
                    log.warning(f"{fn.__name__} attempt {attempt} failed: {exc}. Retrying in {delay:.1f}s")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            return None
        return wrapper
    return decorator
