"""
meandra.logging.context
=======================

Execution context for structured logging.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class LogContext:
    """
    Execution context for workflow logging.

    Stores information about the current execution state for
    injection into log messages.

    Attributes
    ----------
    run_id : Optional[str]
        Unique identifier for the current run.
    workflow_name : Optional[str]
        Name of the currently executing workflow.
    node_name : Optional[str]
        Name of the currently executing node.
    start_time : Optional[float]
        Unix timestamp when execution started.
    """

    run_id: Optional[str] = None
    workflow_name: Optional[str] = None
    node_name: Optional[str] = None
    start_time: Optional[float] = field(default_factory=time.time)

    @property
    def elapsed_seconds(self) -> float:
        """Return elapsed time since start in seconds."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def with_node(self, node_name: str) -> "LogContext":
        """Create a new context with the specified node."""
        return LogContext(
            run_id=self.run_id,
            workflow_name=self.workflow_name,
            node_name=node_name,
            start_time=self.start_time,
        )

    def with_workflow(self, workflow_name: str, run_id: str) -> "LogContext":
        """Create a new context with workflow information."""
        return LogContext(
            run_id=run_id,
            workflow_name=workflow_name,
            node_name=None,
            start_time=time.time(),
        )

    @classmethod
    def current(cls) -> "LogContext":
        """Get the current context."""
        return _current_context.get()

    @classmethod
    def set_current(cls, context: "LogContext") -> None:
        """Set the current context."""
        _current_context.set(context)

    @classmethod
    def clear(cls) -> None:
        """Clear the current context."""
        _current_context.set(LogContext())


# Thread-local context variable
_current_context: ContextVar[LogContext] = ContextVar(
    "meandra_log_context",
    default=LogContext(),
)


class LogContextManager:
    """
    Context manager for scoped log context.

    Examples
    --------
    >>> with LogContextManager(workflow_name="my_workflow", run_id="abc123"):
    ...     logger.info("Inside workflow context")
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        node_name: Optional[str] = None,
    ) -> None:
        self.new_context = LogContext(
            run_id=run_id,
            workflow_name=workflow_name,
            node_name=node_name,
        )
        self._previous: Optional[LogContext] = None

    def __enter__(self) -> LogContext:
        self._previous = LogContext.current()
        LogContext.set_current(self.new_context)
        return self.new_context

    def __exit__(self, *args) -> None:
        if self._previous is not None:
            LogContext.set_current(self._previous)
