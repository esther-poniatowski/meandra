"""
meandra.monitoring.retry
========================

Retry utilities with exponential backoff.
"""

import logging
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

from meandra.core.errors import RetryExhaustedError


logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes
    ----------
    max_attempts : int
        Maximum number of attempts (including initial attempt).
    base_delay : float
        Initial delay between retries in seconds.
    max_delay : float
        Maximum delay between retries in seconds.
    exponential_base : float
        Base for exponential backoff calculation.
    jitter : bool
        Whether to add random jitter to delays.
    retryable_exceptions : Tuple[Type[Exception], ...]
        Exception types that should trigger a retry.
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for the given attempt number.

        Uses exponential backoff with optional jitter.

        Parameters
        ----------
        attempt : int
            The attempt number (1-indexed).

        Returns
        -------
        float
            Delay in seconds before next attempt.
        """
        delay = min(
            self.base_delay * (self.exponential_base ** (attempt - 1)),
            self.max_delay,
        )

        if self.jitter:
            # Add jitter: random value between 0 and 50% of delay
            delay = delay * (1 + random.random() * 0.5)

        return delay


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that retries a function with exponential backoff.

    Parameters
    ----------
    max_attempts : int
        Maximum number of attempts (including initial attempt). Default 3.
    base_delay : float
        Initial delay between retries in seconds. Default 1.0.
    max_delay : float
        Maximum delay between retries in seconds. Default 60.0.
    exponential_base : float
        Base for exponential backoff calculation. Default 2.0.
    jitter : bool
        Whether to add random jitter to delays. Default True.
    retryable_exceptions : Tuple[Type[Exception], ...]
        Exception types that should trigger a retry. Default (Exception,).
    on_retry : Optional[Callable[[int, Exception, float], None]]
        Callback called before each retry with (attempt, exception, delay).

    Returns
    -------
    Callable
        Decorated function with retry behavior.

    Examples
    --------
    >>> @retry(max_attempts=3, base_delay=0.1)
    ... def flaky_operation():
    ...     # May fail intermittently
    ...     pass

    >>> @retry(retryable_exceptions=(ConnectionError, TimeoutError))
    ... def network_call():
    ...     # Only retry on connection/timeout errors
    ...     pass
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return execute_with_retry(func, config, on_retry, *args, **kwargs)

        return wrapper

    return decorator


def execute_with_retry(
    func: Callable[..., T],
    config: RetryConfig,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Execute a function with retry logic.

    Parameters
    ----------
    func : Callable
        Function to execute.
    config : RetryConfig
        Retry configuration.
    on_retry : Optional[Callable[[int, Exception, float], None]]
        Callback called before each retry.
    *args, **kwargs
        Arguments to pass to the function.

    Returns
    -------
    T
        Return value of the function.

    Raises
    ------
    RetryExhaustedError
        If all retry attempts are exhausted.
    Exception
        If a non-retryable exception is raised.
    """
    last_error: Optional[Exception] = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except config.retryable_exceptions as e:
            last_error = e

            if attempt >= config.max_attempts:
                logger.error(
                    f"All {config.max_attempts} attempts exhausted for {func.__name__}: {e}"
                )
                raise RetryExhaustedError(
                    f"All {config.max_attempts} attempts exhausted for {func.__name__}",
                    attempts=attempt,
                    last_error=e,
                ) from e

            delay = config.calculate_delay(attempt)
            logger.warning(
                f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )

            if on_retry:
                on_retry(attempt, e, delay)

            time.sleep(delay)
        except Exception:
            # Non-retryable exception, re-raise immediately
            raise

    # Should not reach here, but satisfy type checker
    assert last_error is not None
    raise RetryExhaustedError(
        f"All {config.max_attempts} attempts exhausted",
        attempts=config.max_attempts,
        last_error=last_error,
    )


class RetryContext:
    """
    Context manager for retryable code blocks.

    Examples
    --------
    >>> config = RetryConfig(max_attempts=3)
    >>> with RetryContext(config) as ctx:
    ...     for attempt in ctx:
    ...         try:
    ...             result = risky_operation()
    ...             break  # Success
    ...         except Exception as e:
    ...             ctx.record_failure(e)
    """

    def __init__(self, config: RetryConfig) -> None:
        self.config = config
        self._attempt = 0
        self._last_error: Optional[Exception] = None
        self._exhausted = False

    def __enter__(self) -> "RetryContext":
        return self

    def __exit__(self, *args) -> None:
        pass

    def __iter__(self) -> "RetryContext":
        self._attempt = 0
        return self

    def __next__(self) -> int:
        if self._exhausted:
            if self._last_error:
                raise RetryExhaustedError(
                    f"All {self.config.max_attempts} attempts exhausted",
                    attempts=self._attempt,
                    last_error=self._last_error,
                )
            raise StopIteration

        self._attempt += 1
        if self._attempt > self.config.max_attempts:
            if self._last_error:
                raise RetryExhaustedError(
                    f"All {self.config.max_attempts} attempts exhausted",
                    attempts=self._attempt - 1,
                    last_error=self._last_error,
                )
            raise StopIteration

        return self._attempt

    def record_failure(self, error: Exception) -> None:
        """Record a failure and wait before next attempt."""
        self._last_error = error

        if self._attempt >= self.config.max_attempts:
            self._exhausted = True
            return

        if not isinstance(error, self.config.retryable_exceptions):
            self._exhausted = True
            raise error

        delay = self.config.calculate_delay(self._attempt)
        logger.warning(
            f"Attempt {self._attempt}/{self.config.max_attempts} failed: {error}. "
            f"Retrying in {delay:.2f}s..."
        )
        time.sleep(delay)
