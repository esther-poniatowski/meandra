"""
meandra.core.errors
====================

Custom exception hierarchy for Meandra.

All Meandra-specific exceptions inherit from MeandraError, enabling
unified error handling across the framework.

Classes
-------
MeandraError
    Base exception for all Meandra errors.
WorkflowError
    Base for workflow-related errors.
NodeExecutionError
    Raised when a node fails during execution.
DependencyResolutionError
    Raised when dependencies cannot be resolved.
ValidationError
    Raised when validation fails.
CheckpointError
    Raised when checkpoint operations fail.
TimeoutError
    Raised when an operation exceeds its time limit.
ConfigurationError
    Raised when configuration is invalid.
"""

from typing import Any, Dict, List, Optional
import builtins


class MeandraError(Exception):
    """
    Base exception for all Meandra errors.

    All Meandra-specific exceptions inherit from this class, enabling
    unified error handling and structured error information.

    Parameters
    ----------
    message : str
        Human-readable error message.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    message : str
        Human-readable error message.
    details : Dict[str, Any]
        Additional structured information about the error.
    """

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            detail_str = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for structured logging.

        Returns
        -------
        Dict[str, Any]
            Structured error representation.
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            **self.details,
        }


class WorkflowError(MeandraError):
    """
    Base exception for workflow-related errors.

    Parameters
    ----------
    message : str
        Human-readable error message.
    workflow_name : str
        Name of the workflow that encountered the error.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    workflow_name : str
        Name of the workflow that encountered the error.
    """

    def __init__(self, message: str, workflow_name: str, **details: Any) -> None:
        super().__init__(message, workflow_name=workflow_name, **details)
        self.workflow_name = workflow_name


class NodeExecutionError(WorkflowError):
    """
    Raised when a node fails during execution.

    Parameters
    ----------
    message : str
        Human-readable error message.
    workflow_name : str
        Name of the workflow that encountered the error.
    node_name : str
        Name of the node that failed.
    original_error : Optional[Exception]
        The underlying exception that caused the failure.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    node_name : str
        Name of the node that failed.
    original_error : Exception
        The underlying exception that caused the failure.
    """

    def __init__(
        self,
        message: str,
        workflow_name: str,
        node_name: str,
        original_error: Optional[Exception] = None,
        **details: Any,
    ) -> None:
        super().__init__(
            message,
            workflow_name=workflow_name,
            node_name=node_name,
            **details,
        )
        self.node_name = node_name
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for structured logging.

        Returns
        -------
        Dict[str, Any]
            Structured error representation.
        """
        result = super().to_dict()
        if self.original_error:
            result["original_error"] = {
                "type": type(self.original_error).__name__,
                "message": str(self.original_error),
            }
        return result


class DependencyResolutionError(WorkflowError):
    """
    Raised when workflow dependencies cannot be resolved.

    Parameters
    ----------
    message : str
        Human-readable error message.
    workflow_name : str
        Name of the workflow that encountered the error.
    cycle : Optional[List[str]]
        List of node names involved in a dependency cycle, if applicable.
    missing : Optional[List[str]]
        List of missing dependency names, if applicable.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    cycle : List[str]
        List of node names involved in a dependency cycle, if applicable.
    missing : List[str]
        List of missing dependency names, if applicable.
    """

    def __init__(
        self,
        message: str,
        workflow_name: str,
        cycle: Optional[List[str]] = None,
        missing: Optional[List[str]] = None,
        **details: Any,
    ) -> None:
        super().__init__(
            message,
            workflow_name=workflow_name,
            **details,
        )
        self.cycle = cycle or []
        self.missing = missing or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for structured logging.

        Returns
        -------
        Dict[str, Any]
            Structured error representation.
        """
        result = super().to_dict()
        if self.cycle:
            result["cycle"] = self.cycle
        if self.missing:
            result["missing"] = self.missing
        return result


class ValidationError(WorkflowError):
    """
    Raised when workflow validation fails.

    Parameters
    ----------
    message : str
        Human-readable error message.
    workflow_name : str
        Name of the workflow that encountered the error.
    errors : Optional[List[str]]
        List of validation error messages.
    warnings : Optional[List[str]]
        List of validation warning messages.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    errors : List[str]
        List of validation error messages.
    warnings : List[str]
        List of validation warning messages.
    """

    def __init__(
        self,
        message: str,
        workflow_name: str,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        **details: Any,
    ) -> None:
        super().__init__(
            message,
            workflow_name=workflow_name,
            **details,
        )
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for structured logging.

        Returns
        -------
        Dict[str, Any]
            Structured error representation.
        """
        result = super().to_dict()
        result["errors"] = self.errors
        result["warnings"] = self.warnings
        return result


class CheckpointError(MeandraError):
    """
    Raised when checkpoint operations fail.

    Parameters
    ----------
    message : str
        Human-readable error message.
    operation : str
        The checkpoint operation that failed (e.g., 'save', 'load', 'delete').
    checkpoint_id : Optional[str]
        ID of the checkpoint involved, if applicable.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    operation : str
        The checkpoint operation that failed (e.g., 'save', 'load', 'delete').
    checkpoint_id : Optional[str]
        ID of the checkpoint involved, if applicable.
    """

    def __init__(
        self,
        message: str,
        operation: str,
        checkpoint_id: Optional[str] = None,
        **details: Any,
    ) -> None:
        super().__init__(
            message,
            operation=operation,
            checkpoint_id=checkpoint_id,
            **details,
        )
        self.operation = operation
        self.checkpoint_id = checkpoint_id


class TimeoutError(builtins.TimeoutError, MeandraError):
    """
    Raised when an operation exceeds its time limit.

    Parameters
    ----------
    message : str
        Human-readable error message.
    timeout_seconds : float
        The timeout that was exceeded.
    operation : str
        Description of the operation that timed out.
    elapsed_seconds : Optional[float]
        Actual elapsed time before timeout, if known.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    timeout_seconds : float
        The timeout that was exceeded.
    elapsed_seconds : Optional[float]
        Actual elapsed time before timeout, if known.
    operation : str
        Description of the operation that timed out.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        operation: str,
        elapsed_seconds: Optional[float] = None,
        **details: Any,
    ) -> None:
        MeandraError.__init__(
            self,
            message,
            timeout_seconds=timeout_seconds,
            operation=operation,
            elapsed_seconds=elapsed_seconds,
            **details,
        )
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        self.operation = operation


class ConfigurationError(MeandraError):
    """
    Raised when configuration is invalid or missing.

    Parameters
    ----------
    message : str
        Human-readable error message.
    config_key : Optional[str]
        The configuration key that caused the error, if applicable.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    config_key : Optional[str]
        The configuration key that caused the error, if applicable.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **details: Any,
    ) -> None:
        super().__init__(message, config_key=config_key, **details)
        self.config_key = config_key


class RetryExhaustedError(MeandraError):
    """
    Raised when all retry attempts have been exhausted.

    Parameters
    ----------
    message : str
        Human-readable error message.
    attempts : int
        Number of attempts made.
    last_error : Exception
        The last exception that occurred.
    **details : Any
        Additional structured error information.

    Attributes
    ----------
    attempts : int
        Number of attempts made.
    last_error : Exception
        The last exception that occurred.
    """

    def __init__(
        self,
        message: str,
        attempts: int,
        last_error: Exception,
        **details: Any,
    ) -> None:
        super().__init__(message, attempts=attempts, **details)
        self.attempts = attempts
        self.last_error = last_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for structured logging.

        Returns
        -------
        Dict[str, Any]
            Structured error representation.
        """
        result = super().to_dict()
        result["last_error"] = {
            "type": type(self.last_error).__name__,
            "message": str(self.last_error),
        }
        return result
