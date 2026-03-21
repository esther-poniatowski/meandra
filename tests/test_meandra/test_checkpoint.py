"""
Tests for checkpoint functionality.
"""

import pytest
import tempfile
from pathlib import Path

from meandra import (
    CheckpointManager,
    FileSystemStorage,
)


class TestFileSystemStorage:
    """Tests for FileSystemStorage."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a temporary storage."""
        return FileSystemStorage(tmp_path)

    def test_save_and_load(self, storage):
        """Test basic save and load."""
        data = {"key": "value", "numbers": [1, 2, 3]}
        checkpoint_id = storage.save("test_workflow", "node1", 0, data, "run_001")

        loaded = storage.load(checkpoint_id)
        assert loaded == data

    def test_list_checkpoints(self, storage):
        """Test listing checkpoints."""
        storage.save("test_workflow", "node1", 0, {"a": 1}, "run_001")
        storage.save("test_workflow", "node2", 1, {"b": 2}, "run_001")

        checkpoints = storage.list_checkpoints("test_workflow")
        assert len(checkpoints) == 2

    def test_list_checkpoints_empty(self, storage):
        """Test listing checkpoints for non-existent workflow."""
        checkpoints = storage.list_checkpoints("nonexistent")
        assert checkpoints == []

    def test_delete_checkpoint(self, storage):
        """Test deleting a checkpoint."""
        checkpoint_id = storage.save("test_workflow", "node1", 0, {"a": 1}, "run_001")

        storage.delete(checkpoint_id)

        assert storage.get_metadata(checkpoint_id) is None

    def test_get_metadata(self, storage):
        """Test getting checkpoint metadata."""
        checkpoint_id = storage.save("test_workflow", "node1", 5, {"a": 1}, "run_xyz")

        metadata = storage.get_metadata(checkpoint_id)
        assert metadata is not None
        assert metadata.workflow_name == "test_workflow"
        assert metadata.node_name == "node1"
        assert metadata.node_index == 5
        assert metadata.run_id == "run_xyz"

    def test_retention_policy(self, tmp_path):
        """Test retention policy deletes old checkpoints."""
        storage = FileSystemStorage(tmp_path, retention=2)

        storage.save("test_workflow", "node1", 0, {"a": 1}, "run_001")
        storage.save("test_workflow", "node2", 1, {"b": 2}, "run_002")
        storage.save("test_workflow", "node3", 2, {"c": 3}, "run_003")

        checkpoints = storage.list_checkpoints("test_workflow")
        assert len(checkpoints) == 2


class TestCheckpointManager:
    """Tests for CheckpointManager."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a checkpoint manager with temporary storage."""
        return CheckpointManager.with_filesystem(str(tmp_path), retention=5)

    def test_save_and_load(self, manager):
        """Test basic save and load."""
        data = {"output": [1, 2, 3]}
        context = {"prev_output": "value"}

        checkpoint_id = manager.save(
            "my_workflow", "node1", 0, data, "run_001", context=context
        )

        checkpoint = manager.load(checkpoint_id)
        assert checkpoint is not None
        assert checkpoint.data == data
        assert checkpoint.context == context
        assert checkpoint.info.workflow_name == "my_workflow"
        assert checkpoint.info.node_name == "node1"

    def test_load_latest(self, manager):
        """Test loading the latest checkpoint."""
        manager.save("my_workflow", "node1", 0, {"a": 1}, "run_001")
        manager.save("my_workflow", "node2", 1, {"b": 2}, "run_001")

        latest = manager.load_latest("my_workflow")
        assert latest is not None
        # Latest should be node2 (most recent)
        assert latest.data == {"b": 2}

    def test_load_latest_empty(self, manager):
        """Test loading latest when no checkpoints exist."""
        latest = manager.load_latest("nonexistent")
        assert latest is None

    def test_load_for_run(self, manager):
        """Test loading checkpoint for specific run."""
        manager.save("my_workflow", "node1", 0, {"a": 1}, "run_001")
        manager.save("my_workflow", "node1", 0, {"b": 2}, "run_002")

        checkpoint = manager.load_for_run("my_workflow", "run_001")
        assert checkpoint is not None
        assert checkpoint.data == {"a": 1}

    def test_clear_workflow(self, manager):
        """Test clearing all checkpoints for a workflow."""
        manager.save("my_workflow", "node1", 0, {"a": 1}, "run_001")
        manager.save("my_workflow", "node2", 1, {"b": 2}, "run_001")

        count = manager.clear_workflow("my_workflow")
        assert count == 2

        checkpoints = manager.list_checkpoints("my_workflow")
        assert len(checkpoints) == 0
