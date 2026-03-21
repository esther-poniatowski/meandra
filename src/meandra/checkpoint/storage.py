"""
meandra.checkpoint.storage
==========================

Storage backends for checkpoints.
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
    """Metadata for a checkpoint."""

    workflow_name: str
    node_name: str
    node_index: int
    run_id: str
    timestamp: str
    data_path: str
    workflow_hash: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "node_name": self.node_name,
            "node_index": self.node_index,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "data_path": self.data_path,
            "workflow_hash": self.workflow_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CheckpointMetadata":
        """Create from dictionary."""
        return cls(
            workflow_name=data["workflow_name"],
            node_name=data["node_name"],
            node_index=data["node_index"],
            run_id=data["run_id"],
            timestamp=data["timestamp"],
            data_path=data["data_path"],
            workflow_hash=data.get("workflow_hash"),
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
    base_dir : str or Path
        Base directory for checkpoint storage.
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
        """Get directory for a workflow's checkpoints."""
        return self.base_dir / workflow_name

    def _generate_checkpoint_id(self, workflow_name: str, run_id: str) -> str:
        """Generate a unique checkpoint ID."""
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
    ) -> str:
        """Save checkpoint data to filesystem."""
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
            workflow_name=workflow_name,
            node_name=node_name,
            node_index=node_index,
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            data_path=str(data_path),
            workflow_hash=workflow_hash,
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
        """Load checkpoint data from filesystem."""
        metadata = self.get_metadata(checkpoint_id)
        if metadata is None:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")

        data_path = Path(metadata.data_path)
        with gzip.open(data_path, "rb") as f:
            data = pickle.load(f)

        logger.info(f"Loaded checkpoint: {checkpoint_id}")
        return data

    def list_checkpoints(self, workflow_name: str) -> List[CheckpointMetadata]:
        """List all checkpoints for a workflow."""
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
        """Delete a checkpoint from filesystem."""
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
        """Get metadata for a checkpoint."""
        for workflow_dir in self.base_dir.iterdir():
            if workflow_dir.is_dir():
                checkpoint_dir = workflow_dir / checkpoint_id
                metadata_path = checkpoint_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        return CheckpointMetadata.from_dict(json.load(f))
        return None

    def _apply_retention(self, workflow_name: str) -> None:
        """Apply retention policy - keep only N most recent checkpoints."""
        checkpoints = self.list_checkpoints(workflow_name)
        if len(checkpoints) > self.retention:
            # Delete oldest checkpoints
            for metadata in checkpoints[self.retention :]:
                checkpoint_id = Path(metadata.data_path).parent.name
                self.delete(checkpoint_id)
