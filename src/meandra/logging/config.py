"""
meandra.logging.config
======================

Logging configuration and utilities.
"""

import logging
import sys
from enum import Enum
from typing import Optional, TextIO

from meandra.logging.context import LogContext
from meandra.core.errors import MeandraError


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """
    Formatter that includes structured context in log messages.

    Injects workflow execution context (run_id, workflow_name, node_name)
    when available.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        include_context: bool = True,
    ) -> None:
        if fmt is None:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt, datefmt)
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        # Inject context if available
        if self.include_context:
            ctx = LogContext.current()
            if ctx.run_id:
                record.msg = f"[run={ctx.run_id}] {record.msg}"
            if ctx.workflow_name:
                record.msg = f"[wf={ctx.workflow_name}] {record.msg}"
            if ctx.node_name:
                record.msg = f"[node={ctx.node_name}] {record.msg}"

        if record.exc_info:
            exc = record.exc_info[1]
            if isinstance(exc, MeandraError) or hasattr(exc, "to_dict"):
                try:
                    error_dict = exc.to_dict()  # type: ignore[call-arg]
                    record.msg = f"{record.msg} | error={error_dict}"
                except Exception:
                    pass

        return super().format(record)


def configure_logging(
    level: LogLevel | str = LogLevel.INFO,
    stream: Optional[TextIO] = None,
    log_file: Optional[str] = None,
    include_context: bool = True,
    format_string: Optional[str] = None,
) -> None:
    """
    Configure logging for Meandra.

    Parameters
    ----------
    level : LogLevel | str
        Minimum log level. Default is INFO.
    stream : Optional[TextIO]
        Stream for console output. Default is sys.stderr.
    log_file : Optional[str]
        Path to log file. If provided, logs are also written to file.
    include_context : bool
        Whether to include workflow context in log messages. Default True.
    format_string : Optional[str]
        Custom format string. If None, uses structured format.

    Examples
    --------
    >>> from meandra.logging import configure_logging, LogLevel
    >>> configure_logging(level=LogLevel.DEBUG, log_file="workflow.log")
    """
    if isinstance(level, str):
        level = LogLevel(level.upper())

    # Get meandra root logger
    logger = logging.getLogger("meandra")
    logger.setLevel(getattr(logging, level.value))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = StructuredFormatter(fmt=format_string, include_context=include_context)

    # Console handler
    console_handler = logging.StreamHandler(stream or sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a Meandra module.

    Parameters
    ----------
    name : str
        Logger name (typically __name__ of the module).

    Returns
    -------
    logging.Logger
        Configured logger instance.

    Examples
    --------
    >>> from meandra.logging import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing started")
    """
    if not name.startswith("meandra"):
        name = f"meandra.{name}"
    return logging.getLogger(name)
