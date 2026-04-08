"""
Meandra: Workflow orchestration for data pipelines.

This package provides tools for building and executing data processing pipelines:

- **Core**: Node and Workflow definitions for pipeline structure
- **Scheduling**: DAG-based dependency resolution
- **Orchestration**: Workflow execution with state tracking
- **Datastore**: I/O handlers and data catalog for multiple file formats
- **Checkpoint**: Workflow state persistence and resumption
- **Monitoring**: Execution state tracking and logging

Example
-------
>>> from meandra import Node, Workflow, SchedulingOrchestrator
>>>
>>> def load_data(inputs):
...     return {"data": [1, 2, 3]}
>>>
>>> def process(inputs):
...     return {"result": sum(inputs["data"])}
>>>
>>> wf = Workflow("example")
>>> wf.add_node(Node("loader", load_data, outputs=["data"]))
>>> wf.add_node(Node("processor", process, dependencies=["loader"], inputs=["data"], outputs=["result"]))
>>>
>>> orchestrator = SchedulingOrchestrator()
>>> results = orchestrator.run(wf, {})
>>> results["result"]
6
"""

from importlib.metadata import version, PackageNotFoundError
import platform

try:
    if __package__ is None:
        raise PackageNotFoundError
    __version__ = version(__package__)
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

# Core
from meandra.core.node import Node
from meandra.core.workflow import (
    Workflow,
    WorkflowModel,
    ValidationResult,
)
from meandra.core.errors import (
    MeandraError,
    WorkflowError,
    ValidationError,
    DependencyResolutionError,
    NodeExecutionError,
    CheckpointError,
    ConfigurationError,
    RetryExhaustedError,
)

# Scheduling
from meandra.scheduling.scheduler import (
    Scheduler,
    DAGScheduler,
)

# Orchestration
from meandra.orchestration.orchestrator import (
    Orchestrator,
    SchedulingOrchestrator,
    WorkflowExecutionError,
    HookEvent,
)

# Monitoring
from meandra.monitoring.state_tracker import (
    StateTracker,
    InMemoryStateTracker,
    FileStateTracker,
    NodeState,
    NodeExecution,
)

# Datastore
from meandra.datastore.io_handlers import (
    IOHandler,
    PickleHandler,
    NumpyHandler,
    JSONHandler,
    YAMLHandler,
    HandlerRegistry,
    get_handler,
    register_default_handlers,
    read_file,
    write_file,
)
from meandra.datastore.catalog import (
    DataCatalog,
    DatasetEntry,
)

# Checkpoint
from meandra.checkpoint.manager import (
    CheckpointManager,
    Checkpoint,
    CheckpointInfo,
)
from meandra.checkpoint.storage import (
    CheckpointStorage,
    FileSystemStorage,
)
from meandra.api import pipe, step, StepBuilder, PipelineBuilder
from meandra.configuration.mod import ConfigProvider

# Integration (optional - may require tessara/morpha)
try:
    from meandra.integration.tessara import TessaraNodeAdapter, SweepOrchestrator
    from meandra.integration.data import DataStructureIOHandler, create_typed_node
    _INTEGRATION_AVAILABLE = True
except ImportError:
    _INTEGRATION_AVAILABLE = False

__all__ = [
    # Version
    "__version__",
    "info",
    # Core
    "Node",
    "Workflow",
    "WorkflowModel",
    "ValidationResult",
    # Error hierarchy
    "MeandraError",
    "WorkflowError",
    "ValidationError",
    "DependencyResolutionError",
    "NodeExecutionError",
    "CheckpointError",
    "ConfigurationError",
    "RetryExhaustedError",
    # Scheduling
    "Scheduler",
    "DAGScheduler",
    # Orchestration
    "Orchestrator",
    "SchedulingOrchestrator",
    "WorkflowExecutionError",
    "HookEvent",
    # Monitoring
    "StateTracker",
    "InMemoryStateTracker",
    "FileStateTracker",
    "NodeState",
    "NodeExecution",
    # Datastore
    "IOHandler",
    "PickleHandler",
    "NumpyHandler",
    "JSONHandler",
    "YAMLHandler",
    "HandlerRegistry",
    "get_handler",
    "register_default_handlers",
    "read_file",
    "write_file",
    "DataCatalog",
    "DatasetEntry",
    # Checkpoint
    "CheckpointManager",
    "Checkpoint",
    "CheckpointInfo",
    "CheckpointStorage",
    "FileSystemStorage",
    # API
    "pipe",
    "step",
    "StepBuilder",
    "PipelineBuilder",
    # Configuration
    "ConfigProvider",
    # Integration (optional)
    "TessaraNodeAdapter",
    "SweepOrchestrator",
    "DataStructureIOHandler",
    "create_typed_node",
]


def info() -> str:
    """
    Format diagnostic information on package and platform.

    Returns
    -------
    str
        A string with the package name, version, OS, and Python version.
    """
    return f"{__package__} {__version__} | Platform: {platform.system()} Python {platform.python_version()}"
