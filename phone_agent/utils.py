"""Utility functions for Phone Agent."""

import time
import functools
from typing import Callable, TypeVar, Any
from phone_agent.log import logger

T = TypeVar("T")

def retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator with exponential backoff.

    Args:
        retries: Number of retries.
        delay: Initial delay in seconds.
        backoff: Backoff multiplier.
        exceptions: Tuple of exceptions to catch.

    Returns:
        Decorated function.
    """
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
