"""Utility functions for Phone Agent."""

import os
import time
import functools
from typing import Callable, TypeVar, Any
from phone_agent.log import logger

T = TypeVar("T")

def retry(
    retries: int | None = None,
    delay: float | None = None,
    backoff: float | None = None,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator with exponential backoff.

    Supports configuration via environment variables:
    - PHONE_AGENT_RETRY_COUNT: Number of retries (default: 3)
    - PHONE_AGENT_RETRY_DELAY: Initial delay in seconds (default: 1.0)
    - PHONE_AGENT_RETRY_BACKOFF: Backoff multiplier (default: 2.0)

    Args:
        retries: Number of retries (overrides env var if specified).
        delay: Initial delay in seconds (overrides env var if specified).
        backoff: Backoff multiplier (overrides env var if specified).
        exceptions: Tuple of exceptions to catch.

    Returns:
        Decorated function.
    """
    # Read from environment variables with defaults
    if retries is None:
        retries = int(os.getenv("PHONE_AGENT_RETRY_COUNT", "3"))
    if delay is None:
        delay = float(os.getenv("PHONE_AGENT_RETRY_DELAY", "1.0"))
    if backoff is None:
        backoff = float(os.getenv("PHONE_AGENT_RETRY_BACKOFF", "2.0"))
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_retries = 0
            current_delay = delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    current_retries += 1
                    if current_retries > retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed: {e}. Retrying in {current_delay}s... ({current_retries}/{retries})")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
