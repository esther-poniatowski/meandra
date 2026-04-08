"""
meandra.checkpoint.storage
==========================

Storage backends for checkpoints.

Classes
-------
CheckpointMetadata
    Metadata for a checkpoint.
CheckpointStorage
    Abstract base class for checkpoint storage backends.
FileSystemStorage
    File system-based checkpoint storage.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List
import gzip
import json
import pickle
import logging


logger = logging.getLogger(__name__)


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint.

    Attributes
    ----------
    checkpoint_id : str
        Unique identifier for the checkpoint.
    workflow_name : str
        Name of the workflow.
    node_name : str
        Name of the node that produced the data.
    node_index : int
        Index of the node in execution order.
    run_id : str
        Unique run identifier.
    timestamp : str
        ISO-format timestamp of checkpoint creation.
    data_path : str
        Path to the serialized data file.
    workflow_hash : Optional[str]
        Hash of the workflow definition, or None.
    completed_nodes : List[str]
        Names of nodes completed at checkpoint time.
    """

    checkpoint_id: str
    workflow_name: str
    node_name: str
    node_index: int
    run_id: str
    timestamp: str
    data_path: str
    workflow_hash: Optional[str] = None
    completed_nodes: List[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of the metadata.
        """
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_name": self.workflow_name,
            "node_name": self.node_name,
            "node_index": self.node_index,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "data_path": self.data_path,
            "workflow_hash": self.workflow_hash,
            "completed_nodes": list(self.completed_nodes or []),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CheckpointMetadata":
        """Create from dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing checkpoint metadata fields.

        Returns
        -------
        CheckpointMetadata
            New instance populated from the dictionary.
        """
        return cls(
            checkpoint_id=data.get("checkpoint_id") or Path(data["data_path"]).parent.name,
            workflow_name=data["workflow_name"],
            node_name=data["node_name"],
            node_index=data["node_index"],
            run_id=data["run_id"],
            timestamp=data["timestamp"],
            data_path=data["data_path"],
            workflow_hash=data.get("workflow_hash"),
            completed_nodes=list(data.get("completed_nodes") or [data["node_name"]]),
        )


class CheckpointStorage(ABC):
    """
    Abstract base class for checkpoint storage backends.

    Storage backends handle the persistence of checkpoint data and metadata.
    """

    @abstractmethod
    def save(
        self,
        workflow_name: str,
        node_name: str,
        node_index: int,
        data: Any,
        run_id: str,
        workflow_hash: Optional[str] = None,
        completed_nodes: Optional[List[str]] = None,
    ) -> str:
        """
        Save checkpoint data.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        node_name : str
            Name of the node that produced the data.
        node_index : int
            Index of the node in execution order.
        data : Any
            Data to checkpoint.
        run_id : str
            Unique run identifier.
        workflow_hash : Optional[str]
            Hash of the workflow definition.
        completed_nodes : Optional[List[str]]
            Names of nodes completed so far.

        Returns
        -------
        str
            Checkpoint identifier.
        """
        pass

    @abstractmethod
    def load(self, checkpoint_id: str) -> Any:
        """
        Load checkpoint data.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.

        Returns
        -------
        Any
            Loaded data.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete(self, checkpoint_id: str) -> None:
        """
        Delete a checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.
        """
        pass

    @abstractmethod
    def get_metadata(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """
        Get metadata for a checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.

        Returns
        -------
        Optional[CheckpointMetadata]
            Checkpoint metadata, or None if not found.
        """
        pass


class FileSystemStorage(CheckpointStorage):
    """
    File system-based checkpoint storage.

    Stores checkpoint data as gzip-compressed pickle files with JSON metadata.

    Directory structure:
        base_dir/
            workflow_name/
                checkpoint_<timestamp>_<run_id>/
                    metadata.json
                    data.pkl.gz

    Parameters
    ----------
    base_dir : str | Path
        Base directory for checkpoint storage.
    retention : int
        Number of checkpoints to retain per workflow (0 = unlimited).

    Attributes
    ----------
    base_dir : Path
        Resolved base directory for checkpoint storage.
    retention : int
        Number of checkpoints to retain per workflow (0 = unlimited).

    Examples
    --------
    >>> storage = FileSystemStorage("/tmp/checkpoints", retention=5)
    >>> checkpoint_id = storage.save("my_workflow", "node1", 0, data, "run_001")
    >>> loaded_data = storage.load(checkpoint_id)
    """

    def __init__(self, base_dir: str | Path, retention: int = 0):
        self.base_dir = Path(base_dir)
        self.retention = retention
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_workflow_dir(self, workflow_name: str) -> Path:
        """Get directory for a workflow's checkpoints.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.

        Returns
        -------
        Path
            Directory path for the workflow's checkpoints.
        """
        return self.base_dir / workflow_name

    def _generate_checkpoint_id(self, workflow_name: str, run_id: str) -> str:
        """Generate a unique checkpoint ID.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        run_id : str
            Unique run identifier.

        Returns
        -------
        str
            Generated checkpoint identifier.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"checkpoint_{timestamp}_{run_id}"

    def save(
        self,
        workflow_name: str,
        node_name: str,
        node_index: int,
        data: Any,
        run_id: str,
        workflow_hash: Optional[str] = None,
        completed_nodes: Optional[List[str]] = None,
    ) -> str:
        """Save checkpoint data to filesystem.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        node_name : str
            Name of the node that produced the data.
        node_index : int
            Index of the node in execution order.
        data : Any
            Data to checkpoint.
        run_id : str
            Unique run identifier.
        workflow_hash : Optional[str]
            Hash of the workflow definition.
        completed_nodes : Optional[List[str]]
            Names of nodes completed so far.

        Returns
        -------
        str
            Checkpoint identifier.
        """
        checkpoint_id = self._generate_checkpoint_id(workflow_name, run_id)
        workflow_dir = self._get_workflow_dir(workflow_name)
        checkpoint_dir = workflow_dir / checkpoint_id

        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save data as gzip-compressed pickle
        data_path = checkpoint_dir / "data.pkl.gz"
        with gzip.open(data_path, "wb") as f:
            pickle.dump(data, f)

        # Save metadata as JSON
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            workflow_name=workflow_name,
            node_name=node_name,
            node_index=node_index,
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            data_path=str(data_path),
            workflow_hash=workflow_hash,
            completed_nodes=sorted(completed_nodes or [node_name]),
        )
        metadata_path = checkpoint_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        logger.info(f"Saved checkpoint: {checkpoint_id} for node '{node_name}'")

        # Apply retention policy
        if self.retention > 0:
            self._apply_retention(workflow_name)

        return checkpoint_id

    def load(self, checkpoint_id: str) -> Any:
        """Load checkpoint data from filesystem.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.

        Returns
        -------
        Any
            Loaded data.
        """
        metadata = self.get_metadata(checkpoint_id)
        if metadata is None:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")

        data_path = Path(metadata.data_path)
        with gzip.open(data_path, "rb") as f:
            data = pickle.load(f)

        logger.info(f"Loaded checkpoint: {checkpoint_id}")
        return data

    def list_checkpoints(self, workflow_name: str) -> List[CheckpointMetadata]:
        """List all checkpoints for a workflow.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.

        Returns
        -------
        List[CheckpointMetadata]
            List of checkpoint metadata, sorted by timestamp (newest first).
        """
        workflow_dir = self._get_workflow_dir(workflow_name)
        if not workflow_dir.exists():
            return []

        checkpoints = []
        for checkpoint_dir in workflow_dir.iterdir():
            if checkpoint_dir.is_dir():
                metadata_path = checkpoint_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        metadata = CheckpointMetadata.from_dict(json.load(f))
                        checkpoints.append(metadata)

        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda m: m.timestamp, reverse=True)
        return checkpoints

    def delete(self, checkpoint_id: str) -> None:
        """Delete a checkpoint from filesystem.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.
        """
        # Find the checkpoint directory
        for workflow_dir in self.base_dir.iterdir():
            if workflow_dir.is_dir():
                checkpoint_dir = workflow_dir / checkpoint_id
                if checkpoint_dir.exists():
                    import shutil

                    shutil.rmtree(checkpoint_dir)
                    logger.info(f"Deleted checkpoint: {checkpoint_id}")
                    return

        logger.warning(f"Checkpoint not found for deletion: {checkpoint_id}")

    def get_metadata(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Get metadata for a checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            Checkpoint identifier.

        Returns
        -------
        Optional[CheckpointMetadata]
            Checkpoint metadata, or None if not found.
        """
        for workflow_dir in self.base_dir.iterdir():
            if workflow_dir.is_dir():
                checkpoint_dir = workflow_dir / checkpoint_id
                metadata_path = checkpoint_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        return CheckpointMetadata.from_dict(json.load(f))
        return None

    def _apply_retention(self, workflow_name: str) -> None:
        """Apply retention policy - keep only N most recent checkpoints.

        Parameters
        ----------
        workflow_name : str
            Name of the workflow.
        """
        checkpoints = self.list_checkpoints(workflow_name)
        if len(checkpoints) > self.retention:
            # Delete oldest checkpoints
            for metadata in checkpoints[self.retention :]:
                self.delete(metadata.checkpoint_id)
