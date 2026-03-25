"""
meandra.checkpoint.manager
==========================

Checkpoint management for workflow resumption.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, List
import logging

from meandra.checkpoint.storage import CheckpointStorage, FileSystemStorage, CheckpointMetadata
from meandra.core.errors import CheckpointError

if TYPE_CHECKING:
    from meandra.core.workflow import Workflow


logger = logging.getLogger(__name__)


@dataclass
class CheckpointInfo:
    """Summary information about a checkpoint."""

    checkpoint_id: str
    workflow_name: str
    node_name: str
    node_index: int
    run_id: str
    timestamp: str
    workflow_hash: Optional[str] = None
    completed_nodes: tuple[str, ...] = ()


@dataclass
class Checkpoint:
    """A loaded checkpoint with data and metadata."""

    info: CheckpointInfo
    data: Any
    context: Dict[str, Any]
    state: Dict[str, Dict[str, Any]]


@dataclass(frozen=True)
class ResumePlan:
    """Explicit plan describing how a workflow may safely resume."""

    checkpoint_id: str
    run_id: str
    completed_nodes: tuple[str, ...]
    context: Dict[str, Any]
    state: Dict[str, Dict[str, Any]]


class CheckpointManager:
    """
    Manage workflow checkpoints for resumption.

    The checkpoint manager provides a high-level interface for saving,
    loading, and managing checkpoints during workflow execution.

    Parameters
    ----------
    storage : CheckpointStorage
        Storage backend for checkpoints.

    Examples
    --------
    >>> from meandra.checkpoint import CheckpointManager, FileSystemStorage
    >>> storage = FileSystemStorage("/tmp/checkpoints")
    >>> manager = CheckpointManager(storage)
    >>>
    >>> # Save a checkpoint
    >>> manager.save("my_workflow", "node1", 0, {"output": data}, "run_001")
    >>>
    >>> # Load latest checkpoint
    >>> checkpoint = manager.load_latest("my_workflow")
    >>> if checkpoint:
    ...     print(f"Resuming from node {checkpoint.info.node_name}")
    """

    def __init__(self, storage: CheckpointStorage):
        self.storage = storage

    @classmethod
    def with_filesystem(
        cls, base_dir: str, retention: int = 5
    ) -> "CheckpointManager":
        """
        Create a checkpoint manager with filesystem storage.

        Parameters
        ----------
        base_dir : str
            Base directory for checkpoint storage.
        retention : int
            Number of checkpoints to retain per workflow.

        Returns
        -------
        CheckpointManager
            Manager with FileSystemStorage backend.
        """
        storage = FileSystemStorage(base_dir, retention=retention)
        return cls(storage)

    def save(
        self,
        workflow_name: str,
        node_name: str,
        node_index: int,
        data: Any,
        run_id: str,
        context: Optional[Dict[str, Any]] = None,
        workflow_hash: Optional[str] = None,
        workflow_state: Optional[Dict[str, Dict[str, Any]]] = None,
        completed_nodes: Optional[List[str]] = None,
    ) -> str:
        """
        Save a checkpoint after node execution.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        node_name : str
            Name of the node that produced the data.
        node_index : int
            Index of the node in execution order.
        data : Any
            Node output data to checkpoint.
        run_id : str
            Unique run identifier.
        context : Optional[Dict[str, Any]]
            Full execution context to save for resumption.

        Returns
        -------
        str
            Checkpoint identifier.
        """
        # Package data with context for full resumption capability
        checkpoint_data = {
            "node_output": data,
            "context": context or {},
            "workflow_state": workflow_state or {
                "inputs": {},
                "artifacts": dict(context or {}),
            },
        }

        checkpoint_id = self.storage.save(
            workflow_name=workflow_name,
            node_name=node_name,
            node_index=node_index,
            data=checkpoint_data,
            run_id=run_id,
            workflow_hash=workflow_hash,
            completed_nodes=completed_nodes,
        )

        logger.info(
            f"Checkpoint saved: workflow='{workflow_name}', "
            f"node='{node_name}', id={checkpoint_id}"
        )
        return checkpoint_id

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load a specific checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.

        Returns
        -------
        Optional[Checkpoint]
            Loaded checkpoint, or None if not found.
        """
        try:
            metadata = self.storage.get_metadata(checkpoint_id)
            if metadata is None:
                return None

            checkpoint_data = self.storage.load(checkpoint_id)

            info = CheckpointInfo(
                checkpoint_id=checkpoint_id,
                workflow_name=metadata.workflow_name,
                node_name=metadata.node_name,
                node_index=metadata.node_index,
                run_id=metadata.run_id,
                timestamp=metadata.timestamp,
                workflow_hash=metadata.workflow_hash,
                completed_nodes=tuple(metadata.completed_nodes or (metadata.node_name,)),
            )
            state = checkpoint_data.get("workflow_state") or {
                "inputs": {},
                "artifacts": checkpoint_data.get("context", {}),
            }

            return Checkpoint(
                info=info,
                data=checkpoint_data.get("node_output"),
                context=checkpoint_data.get("context", {}),
                state={
                    "inputs": dict(state.get("inputs", {})),
                    "artifacts": dict(state.get("artifacts", {})),
                },
            )
        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None

    def load_latest(self, workflow_name: str) -> Optional[Checkpoint]:
        """
        Load the most recent checkpoint for a workflow.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.

        Returns
        -------
        Optional[Checkpoint]
            Most recent checkpoint, or None if none exist.
        """
        checkpoints = self.list_checkpoints(workflow_name)
        if not checkpoints:
            return None

        # Get most recent (first in sorted list)
        latest = checkpoints[0]
        return self.load(latest.checkpoint_id)

    def load_for_run(self, workflow_name: str, run_id: str) -> Optional[Checkpoint]:
        """
        Load the most recent checkpoint for a specific run.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        run_id : str
            Run identifier to match.

        Returns
        -------
        Optional[Checkpoint]
            Most recent checkpoint for the run, or None if none exist.
        """
        checkpoints = self.list_checkpoints(workflow_name)
        for metadata in checkpoints:
            if metadata.run_id == run_id:
                return self.load(metadata.checkpoint_id)
        return None

    def list_checkpoints(self, workflow_name: str) -> List[CheckpointMetadata]:
        """
        List all checkpoints for a workflow.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.

        Returns
        -------
        List[CheckpointMetadata]
            List of checkpoint metadata, sorted by timestamp (newest first).
        """
        return self.storage.list_checkpoints(workflow_name)

    def delete(self, checkpoint_id: str) -> None:
        """
        Delete a checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.
        """
        self.storage.delete(checkpoint_id)
        logger.info(f"Deleted checkpoint: {checkpoint_id}")

    def clear_workflow(self, workflow_name: str) -> int:
        """
        Delete all checkpoints for a workflow.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.

        Returns
        -------
        int
            Number of checkpoints deleted.
        """
        checkpoints = self.list_checkpoints(workflow_name)
        count = 0
        for metadata in checkpoints:
            self.storage.delete(metadata.checkpoint_id)
            count += 1

        logger.info(f"Cleared {count} checkpoints for workflow '{workflow_name}'")
        return count

    def build_resume_plan(self, workflow: "Workflow", checkpoint: Checkpoint) -> ResumePlan:
        """Validate checkpoint compatibility and build an explicit resume plan."""
        workflow_hash = workflow.structure_hash()
        if checkpoint.info.workflow_hash != workflow_hash:
            raise CheckpointError(
                "Checkpoint is incompatible with the current workflow structure.",
                operation="resume",
                checkpoint_id=checkpoint.info.checkpoint_id,
            )
        completed_nodes = checkpoint.info.completed_nodes or (checkpoint.info.node_name,)
        unknown = sorted(set(completed_nodes) - set(workflow.nodes))
        if unknown:
            raise CheckpointError(
                f"Checkpoint references unknown completed node(s): {unknown}",
                operation="resume",
                checkpoint_id=checkpoint.info.checkpoint_id,
            )
        return ResumePlan(
            checkpoint_id=checkpoint.info.checkpoint_id,
            run_id=checkpoint.info.run_id,
            completed_nodes=tuple(completed_nodes),
            context=dict(checkpoint.context),
            state={
                "inputs": dict(checkpoint.state.get("inputs", {})),
                "artifacts": dict(checkpoint.state.get("artifacts", {})),
            },
        )
