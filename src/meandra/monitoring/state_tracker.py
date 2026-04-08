"""
meandra.monitoring.state_tracker
================================

Track workflow and node execution state.

Classes
-------
NodeState
    Possible states for a node during execution.
NodeExecution
    Record of a node execution.
StateTracker
    Abstract base class for tracking workflow execution state.
InMemoryStateTracker
    Track execution state in memory.
FileStateTracker
    Persist execution state as JSON lines with query support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
import logging
import json
from pathlib import Path


logger = logging.getLogger(__name__)


class NodeState(str, Enum):
    """Possible states for a node during execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NodeExecution:
    """Record of a node execution.

    Attributes
    ----------
    node_name : str
        Name of the executed node.
    state : NodeState
        Current state of the node.
    start_time : Optional[datetime]
        Timestamp when execution started.
    end_time : Optional[datetime]
        Timestamp when execution ended.
    error : Optional[str]
        Error message if the node failed.
    outputs : Optional[Dict[str, Any]]
        Output data produced by the node.
    """

    node_name: str
    state: NodeState = NodeState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None


class StateTracker(ABC):
    """
    Abstract base class for tracking workflow execution state.

    Tracks the execution state of each node and provides logging
    and recovery capabilities.
    """

    @abstractmethod
    def mark_running(self, node_name: str) -> None:
        """Mark a node as running.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        pass

    @abstractmethod
    def mark_completed(self, node_name: str, outputs: Dict[str, Any]) -> None:
        """Mark a node as completed with outputs.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        outputs : Dict[str, Any]
            Output data produced by the node.
        """
        pass

    @abstractmethod
    def mark_failed(self, node_name: str, error: str) -> None:
        """Mark a node as failed with error message.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        error : str
            Error message describing the failure.
        """
        pass

    @abstractmethod
    def mark_skipped(self, node_name: str) -> None:
        """Mark a node as skipped.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        pass

    @abstractmethod
    def get_state(self, node_name: str) -> NodeState:
        """Get the current state of a node.

        Parameters
        ----------
        node_name : str
            Name of the node to query.

        Returns
        -------
        NodeState
            Current state of the node.
        """
        pass

    @abstractmethod
    def is_completed(self, node_name: str) -> bool:
        """Check if a node has completed successfully.

        Parameters
        ----------
        node_name : str
            Name of the node to check.

        Returns
        -------
        bool
            True if the node completed successfully.
        """
        pass

    @abstractmethod
    def get_completed_nodes(self) -> List[str]:
        """Get list of completed node names.

        Returns
        -------
        List[str]
            Names of all completed nodes.
        """
        pass


class InMemoryStateTracker(StateTracker):
    """
    Track execution state in memory.

    Suitable for single-run workflows where persistence is not needed.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow being tracked.
    run_id : str
        Unique identifier for the current run.

    Attributes
    ----------
    run_id : str
        Unique identifier for the current run.
    workflow_name : str
        Name of the workflow being tracked.
    executions : Dict[str, NodeExecution]
        Mapping of node names to execution records.

    Examples
    --------
    >>> tracker = InMemoryStateTracker("my_workflow", "run_001")
    >>> tracker.mark_running("node_a")
    >>> tracker.get_state("node_a")
    <NodeState.RUNNING: 'running'>
    """

    def __init__(self, workflow_name: str, run_id: str):
        self.workflow_name = workflow_name
        self.run_id = run_id
        self.executions: Dict[str, NodeExecution] = {}
        self.start_time = datetime.now()

    def _get_or_create_execution(self, node_name: str) -> NodeExecution:
        """Get existing execution record or create new one.

        Parameters
        ----------
        node_name : str
            Name of the node.

        Returns
        -------
        NodeExecution
            Execution record for the node.
        """
        if node_name not in self.executions:
            self.executions[node_name] = NodeExecution(node_name=node_name)
        return self.executions[node_name]

    def mark_running(self, node_name: str) -> None:
        """Mark a node as running.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        execution = self._get_or_create_execution(node_name)
        execution.state = NodeState.RUNNING
        execution.start_time = datetime.now()
        logger.info(f"[{self.run_id}] Node '{node_name}' started")

    def mark_completed(self, node_name: str, outputs: Dict[str, Any]) -> None:
        """Mark a node as completed with outputs.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        outputs : Dict[str, Any]
            Output data produced by the node.
        """
        execution = self._get_or_create_execution(node_name)
        execution.state = NodeState.COMPLETED
        execution.end_time = datetime.now()
        execution.outputs = outputs
        duration = (
            (execution.end_time - execution.start_time).total_seconds()
            if execution.start_time
            else 0
        )
        logger.info(f"[{self.run_id}] Node '{node_name}' completed in {duration:.2f}s")

    def mark_failed(self, node_name: str, error: str) -> None:
        """Mark a node as failed with error message.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        error : str
            Error message describing the failure.
        """
        execution = self._get_or_create_execution(node_name)
        execution.state = NodeState.FAILED
        execution.end_time = datetime.now()
        execution.error = error
        logger.error(f"[{self.run_id}] Node '{node_name}' failed: {error}")

    def mark_skipped(self, node_name: str) -> None:
        """Mark a node as skipped.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        execution = self._get_or_create_execution(node_name)
        execution.state = NodeState.SKIPPED
        logger.info(f"[{self.run_id}] Node '{node_name}' skipped")

    def get_state(self, node_name: str) -> NodeState:
        """Get the current state of a node.

        Parameters
        ----------
        node_name : str
            Name of the node to query.

        Returns
        -------
        NodeState
            Current state of the node.
        """
        if node_name not in self.executions:
            return NodeState.PENDING
        return self.executions[node_name].state

    def is_completed(self, node_name: str) -> bool:
        """Check if a node has completed successfully.

        Parameters
        ----------
        node_name : str
            Name of the node to check.

        Returns
        -------
        bool
            True if the node completed successfully.
        """
        return self.get_state(node_name) == NodeState.COMPLETED

    def get_completed_nodes(self) -> List[str]:
        """Get list of completed node names.

        Returns
        -------
        List[str]
            Names of all completed nodes.
        """
        return [
            name
            for name, ex in self.executions.items()
            if ex.state == NodeState.COMPLETED
        ]

    def get_failed_nodes(self) -> List[str]:
        """Get list of failed node names.

        Returns
        -------
        List[str]
            Names of all failed nodes.
        """
        return [
            name for name, ex in self.executions.items() if ex.state == NodeState.FAILED
        ]

    def get_outputs(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Get outputs from a completed node.

        Parameters
        ----------
        node_name : str
            Name of the node to query.

        Returns
        -------
        Optional[Dict[str, Any]]
            Output data from the node, or None if not found.
        """
        if node_name in self.executions:
            return self.executions[node_name].outputs
        return None

    def summary(self) -> Dict[str, Any]:
        """Get summary of execution state.

        Returns
        -------
        Dict[str, Any]
            Dictionary with run metadata and counts.
        """
        return {
            "run_id": self.run_id,
            "workflow": self.workflow_name,
            "start_time": self.start_time.isoformat(),
            "completed": len(self.get_completed_nodes()),
            "failed": len(self.get_failed_nodes()),
            "total": len(self.executions),
        }


class FileStateTracker(StateTracker):
    """
    Persist execution state as JSON lines with query support.

    Each state change is appended to a log file. Query methods parse
    the log file to reconstruct current state.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow being tracked.
    run_id : str
        Unique run identifier.
    path : str or Path
        Path to the log file.

    Attributes
    ----------
    workflow_name : str
        Name of the workflow being tracked.
    run_id : str
        Unique run identifier.
    path : Path
        Path to the log file.

    Examples
    --------
    >>> tracker = FileStateTracker("my_workflow", "run_001", "state.jsonl")
    >>> tracker.mark_running("node_a")
    >>> tracker.mark_completed("node_a", {"result": 42})
    >>> tracker.get_state("node_a")
    <NodeState.COMPLETED: 'completed'>
    """

    def __init__(self, workflow_name: str, run_id: str, path: str | Path):
        self.workflow_name = workflow_name
        self.run_id = run_id
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, record: Dict[str, Any]) -> None:
        """Append a record to the log file.

        Parameters
        ----------
        record : Dict[str, Any]
            Record to write as a JSON line.
        """
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def _read_all_records(self) -> List[Dict[str, Any]]:
        """Read all records from the log file.

        Returns
        -------
        List[Dict[str, Any]]
            All records parsed from the log file.
        """
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _get_latest_states(self) -> Dict[str, NodeState]:
        """Get the latest state for each node from the log.

        Returns
        -------
        Dict[str, NodeState]
            Mapping of node names to their latest state.
        """
        records = self._read_all_records()
        states: Dict[str, NodeState] = {}
        for record in records:
            if record.get("run_id") == self.run_id:
                node_name = record.get("node")
                state_value = record.get("state")
                if node_name and state_value:
                    states[node_name] = NodeState(state_value)
        return states

    def mark_running(self, node_name: str) -> None:
        """Mark a node as running.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        self._write(self._record(node_name, NodeState.RUNNING))

    def mark_completed(self, node_name: str, outputs: Dict[str, Any]) -> None:
        """Mark a node as completed with outputs.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        outputs : Dict[str, Any]
            Output data produced by the node.
        """
        record = self._record(node_name, NodeState.COMPLETED)
        record["outputs"] = outputs
        self._write(record)

    def mark_failed(self, node_name: str, error: str) -> None:
        """Mark a node as failed with error message.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        error : str
            Error message describing the failure.
        """
        record = self._record(node_name, NodeState.FAILED)
        record["error"] = error
        self._write(record)

    def mark_skipped(self, node_name: str) -> None:
        """Mark a node as skipped.

        Parameters
        ----------
        node_name : str
            Name of the node to mark.
        """
        self._write(self._record(node_name, NodeState.SKIPPED))

    def get_state(self, node_name: str) -> NodeState:
        """Get the current state of a node.

        Parameters
        ----------
        node_name : str
            Name of the node to query.

        Returns
        -------
        NodeState
            Current state of the node.
        """
        states = self._get_latest_states()
        return states.get(node_name, NodeState.PENDING)

    def is_completed(self, node_name: str) -> bool:
        """Check if a node has completed successfully.

        Parameters
        ----------
        node_name : str
            Name of the node to check.

        Returns
        -------
        bool
            True if the node completed successfully.
        """
        return self.get_state(node_name) == NodeState.COMPLETED

    def get_completed_nodes(self) -> List[str]:
        """Get list of completed node names.

        Returns
        -------
        List[str]
            Names of all completed nodes.
        """
        states = self._get_latest_states()
        return [name for name, state in states.items() if state == NodeState.COMPLETED]

    def get_failed_nodes(self) -> List[str]:
        """Get list of failed node names.

        Returns
        -------
        List[str]
            Names of all failed nodes.
        """
        states = self._get_latest_states()
        return [name for name, state in states.items() if state == NodeState.FAILED]

    def _record(self, node_name: str, state: NodeState) -> Dict[str, Any]:
        """Create a log record.

        Parameters
        ----------
        node_name : str
            Name of the node.
        state : NodeState
            State to record.

        Returns
        -------
        Dict[str, Any]
            Log record dictionary.
        """
        return {
            "run_id": self.run_id,
            "workflow": self.workflow_name,
            "node": node_name,
            "state": state.value,
            "timestamp": datetime.now().isoformat(),
        }
