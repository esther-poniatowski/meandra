"""
meandra.monitoring.progress
===========================

Progress tracking for workflow execution.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """Status of a node in workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NodeProgress:
    """Progress information for a single node."""

    name: str
    status: NodeStatus = NodeStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Return execution duration in seconds, if completed."""
        if self.start_time is None:
            return None
        end = self.end_time or time.time()
        return end - self.start_time


@dataclass
class ProgressTracker:
    """
    Track progress of workflow execution.

    Provides real-time visibility into workflow execution state,
    including node status, timing, and completion percentage.

    Attributes
    ----------
    workflow_name : str
        Name of the workflow being tracked.
    total_nodes : int
        Total number of nodes in the workflow.
    callbacks : List[Callable]
        Functions to call on progress updates.

    Examples
    --------
    >>> tracker = ProgressTracker("my_workflow", 5)
    >>> tracker.add_callback(lambda t: print(f"Progress: {t.percentage:.0f}%"))
    >>> tracker.start_node("load_data")
    >>> tracker.complete_node("load_data", {"data": [1, 2, 3]})
    Progress: 20%
    """

    workflow_name: str
    total_nodes: int
    nodes: Dict[str, NodeProgress] = field(default_factory=dict)
    callbacks: List[Callable[["ProgressTracker"], None]] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def __post_init__(self) -> None:
        self.start_time = time.time()

    @property
    def completed_count(self) -> int:
        """Return number of completed nodes."""
        return sum(
            1 for n in self.nodes.values()
            if n.status in (NodeStatus.COMPLETED, NodeStatus.SKIPPED)
        )

    @property
    def failed_count(self) -> int:
        """Return number of failed nodes."""
        return sum(1 for n in self.nodes.values() if n.status == NodeStatus.FAILED)

    @property
    def running_count(self) -> int:
        """Return number of currently running nodes."""
        return sum(1 for n in self.nodes.values() if n.status == NodeStatus.RUNNING)

    @property
    def percentage(self) -> float:
        """Return completion percentage (0-100)."""
        if self.total_nodes == 0:
            return 100.0
        return (self.completed_count / self.total_nodes) * 100

    @property
    def elapsed_seconds(self) -> float:
        """Return elapsed time since start in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def is_complete(self) -> bool:
        """Return True if all nodes have been processed."""
        return self.completed_count + self.failed_count >= self.total_nodes

    def add_callback(self, callback: Callable[["ProgressTracker"], None]) -> None:
        """Register a callback to be called on progress updates."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[["ProgressTracker"], None]) -> None:
        """Remove a registered callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify(self) -> None:
        """Notify all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(self)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def start_node(self, node_name: str) -> None:
        """Mark a node as running."""
        self.nodes[node_name] = NodeProgress(
            name=node_name,
            status=NodeStatus.RUNNING,
            start_time=time.time(),
        )
        logger.debug(f"Node '{node_name}' started")
        self._notify()

    def complete_node(
        self, node_name: str, outputs: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark a node as completed."""
        if node_name in self.nodes:
            self.nodes[node_name].status = NodeStatus.COMPLETED
            self.nodes[node_name].end_time = time.time()
        else:
            self.nodes[node_name] = NodeProgress(
                name=node_name,
                status=NodeStatus.COMPLETED,
                end_time=time.time(),
            )

        duration = self.nodes[node_name].duration_seconds
        if duration is not None:
            logger.info(
                f"Node '{node_name}' completed in {duration:.2f}s "
                f"({self.completed_count}/{self.total_nodes})"
            )
        else:
            logger.info(
                f"Node '{node_name}' completed "
                f"({self.completed_count}/{self.total_nodes})"
            )
        self._notify()

    def fail_node(self, node_name: str, error: str) -> None:
        """Mark a node as failed."""
        if node_name in self.nodes:
            self.nodes[node_name].status = NodeStatus.FAILED
            self.nodes[node_name].end_time = time.time()
            self.nodes[node_name].error = error
        else:
            self.nodes[node_name] = NodeProgress(
                name=node_name,
                status=NodeStatus.FAILED,
                end_time=time.time(),
                error=error,
            )

        logger.error(f"Node '{node_name}' failed: {error}")
        self._notify()

    def skip_node(self, node_name: str) -> None:
        """Mark a node as skipped."""
        self.nodes[node_name] = NodeProgress(
            name=node_name,
            status=NodeStatus.SKIPPED,
        )
        logger.debug(f"Node '{node_name}' skipped")
        self._notify()

    def finish(self) -> None:
        """Mark the workflow as finished."""
        self.end_time = time.time()
        status = "completed" if self.failed_count == 0 else "completed with failures"
        logger.info(
            f"Workflow '{self.workflow_name}' {status} in {self.elapsed_seconds:.2f}s "
            f"({self.completed_count} completed, {self.failed_count} failed)"
        )
        self._notify()

    def to_dict(self) -> Dict[str, Any]:
        """Convert progress state to a dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "total_nodes": self.total_nodes,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "running": self.running_count,
            "percentage": self.percentage,
            "elapsed_seconds": self.elapsed_seconds,
            "is_complete": self.is_complete,
            "nodes": {
                name: {
                    "status": node.status.value,
                    "duration_seconds": node.duration_seconds,
                    "error": node.error,
                }
                for name, node in self.nodes.items()
            },
        }

    def summary(self) -> str:
        """Return a human-readable summary string."""
        return (
            f"{self.workflow_name}: {self.percentage:.0f}% "
            f"({self.completed_count}/{self.total_nodes} nodes, "
            f"{self.elapsed_seconds:.1f}s elapsed)"
        )
