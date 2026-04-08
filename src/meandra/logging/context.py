"""
meandra.logging.context
=======================

Execution context for structured logging.

Classes
-------
LogContext
    Execution context for workflow logging.
LogContextManager
    Context manager for scoped log context.
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
        """
        Return elapsed time since start in seconds.

        Returns
        -------
        float
            Elapsed time in seconds.
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def with_node(self, node_name: str) -> "LogContext":
        """
        Create a new context with the specified node.

        Parameters
        ----------
        node_name : str
            Name of the node.

        Returns
        -------
        LogContext
            New context with the node set.
        """
        return LogContext(
            run_id=self.run_id,
            workflow_name=self.workflow_name,
            node_name=node_name,
            start_time=self.start_time,
        )

    def with_workflow(self, workflow_name: str, run_id: str) -> "LogContext":
        """
        Create a new context with workflow information.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        run_id : str
            Unique identifier for the run.

        Returns
        -------
        LogContext
            New context with workflow information.
        """
        return LogContext(
            run_id=run_id,
            workflow_name=workflow_name,
            node_name=None,
            start_time=time.time(),
        )

    @classmethod
    def current(cls) -> "LogContext":
        """
        Get the current context.

        Returns
        -------
        LogContext
            The current log context.
        """
        return _current_context.get()

    @classmethod
    def set_current(cls, context: "LogContext") -> None:
        """
        Set the current context.

        Parameters
        ----------
        context : LogContext
            The context to set as current.
        """
        _current_context.set(context)

    @classmethod
    def clear(cls) -> None:
        """Clear the current context, resetting to defaults."""
        _current_context.set(LogContext())


# Thread-local context variable
_current_context: ContextVar[LogContext] = ContextVar(
    "meandra_log_context",
    default=LogContext(),
)


class LogContextManager:
    """
    Context manager for scoped log context.

    Parameters
    ----------
    run_id : Optional[str]
        Unique identifier for the current run.
    workflow_name : Optional[str]
        Name of the currently executing workflow.
    node_name : Optional[str]
        Name of the currently executing node.

    Attributes
    ----------
    new_context : LogContext
        The context that will be active inside the managed scope.

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
        """
        Enter the context, setting the new log context.

        Returns
        -------
        LogContext
            The new log context.
        """
        self._previous = LogContext.current()
        LogContext.set_current(self.new_context)
        return self.new_context

    def __exit__(self, *args: object) -> None:
        """Restore the previous log context.

        Parameters
        ----------
        *args : object
            Exception information (exc_type, exc_val, exc_tb).
        """
        if self._previous is not None:
            LogContext.set_current(self._previous)
