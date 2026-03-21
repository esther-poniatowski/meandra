"""
meandra.orchestration
=====================

Manages the full execution flow of workflows by coordinating the specialized framework's components.

The `orchestration` module implements the central execution engine, which integrates both the
high-level control of the overall process and the low-level execution of individual components.


Public API
----------
SchedulingOrchestrator
    Default orchestrator for executing workflows.
WorkflowExecutionError
    Error raised for node execution failures.
HookEvent
    Lifecycle hook events.
Orchestrator
    Base orchestrator interface.
"""

from meandra.orchestration.orchestrator import (
    Orchestrator,
    SchedulingOrchestrator,
    WorkflowExecutionError,
    HookEvent,
)

__all__ = [
    "Orchestrator",
    "SchedulingOrchestrator",
    "WorkflowExecutionError",
    "HookEvent",
]
