"""
test_meandra.test_monitoring.test_retry
=======================================

Tests for meandra.monitoring.retry module.
"""

import pytest
import time

from meandra.core.errors import RetryExhaustedError
from meandra.monitoring.retry import (
    RetryConfig,
    retry,
    execute_with_retry,
    RetryContext,
)


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        assert config.calculate_delay(1) == 1.0
        assert config.calculate_delay(2) == 2.0
        assert config.calculate_delay(3) == 4.0
        assert config.calculate_delay(4) == 8.0

    def test_calculate_delay_max_cap(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(base_delay=10.0, max_delay=30.0, jitter=False)
        assert config.calculate_delay(5) == 30.0  # Would be 160 without cap

    def test_calculate_delay_with_jitter(self):
        """Test that jitter adds variation."""
        config = RetryConfig(base_delay=1.0, jitter=True)
        delays = [config.calculate_delay(1) for _ in range(10)]
        # All delays should be >= base_delay
        assert all(d >= 1.0 for d in delays)
        # Some variation should exist (unlikely all exactly 1.0)
        assert len(set(delays)) > 1


class TestRetryDecorator:
    """Tests for @retry decorator."""

    def test_successful_on_first_attempt(self):
        """Test function that succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "success"

        result = succeed()
        assert result == "success"
        assert call_count == 1

    def test_retry_then_succeed(self):
        """Test function that fails then succeeds."""
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01)
        def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3

    def test_all_attempts_exhausted(self):
        """Test that RetryExhaustedError is raised after all attempts."""
        call_count = 0

        @retry(max_attempts=3, base_delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(RetryExhaustedError) as exc_info:
            always_fail()

        assert exc_info.value.attempts == 3
        assert isinstance(exc_info.value.last_error, ValueError)
        assert call_count == 3

    def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are raised immediately."""
        call_count = 0

        @retry(max_attempts=3, retryable_exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            raise_type_error()

        assert call_count == 1

    def test_on_retry_callback(self):
        """Test that on_retry callback is called."""
        retry_info = []

        def callback(attempt, error, delay):
            retry_info.append((attempt, str(error), delay))

        call_count = 0

        @retry(max_attempts=3, base_delay=0.01, on_retry=callback)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count}")
            return "ok"

        fail_twice()
        assert len(retry_info) == 2
        assert retry_info[0][0] == 1
        assert "Attempt 1" in retry_info[0][1]


class TestExecuteWithRetry:
    """Tests for execute_with_retry function."""

    def test_execute_with_config(self):
        """Test executing with explicit config."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        call_count = 0

        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail once")
            return "done"

        result = execute_with_retry(flaky, config)
        assert result == "done"
        assert call_count == 2


class TestRetryContext:
    """Tests for RetryContext context manager."""

    def test_successful_first_attempt(self):
        """Test context manager with successful first attempt."""
        config = RetryConfig(max_attempts=3)
        attempts = 0

        with RetryContext(config) as ctx:
            for attempt in ctx:
                attempts = attempt
                break  # Success on first attempt

        assert attempts == 1

    def test_retry_then_succeed(self):
        """Test context manager with retry then success."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        attempts = 0

        with RetryContext(config) as ctx:
            for attempt in ctx:
                attempts = attempt
                if attempt < 3:
                    ctx.record_failure(ValueError("Temporary"))
                else:
                    break  # Success

        assert attempts == 3

    def test_all_attempts_exhausted_context(self):
        """Test context manager with all attempts exhausted."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)

        with pytest.raises(RetryExhaustedError):
            with RetryContext(config) as ctx:
                for _ in ctx:
                    ctx.record_failure(ValueError("Always fails"))


if __name__ == "__main__":
    pytest.main()
