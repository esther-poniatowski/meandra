"""
Tests for state tracking functionality.
"""

import pytest
import json
from pathlib import Path

from meandra import (
    InMemoryStateTracker,
    FileStateTracker,
    NodeState,
    NodeExecution,
)


class TestNodeExecution:
    """Tests for NodeExecution dataclass."""

    def test_default_values(self):
        """Test default values for NodeExecution."""
        execution = NodeExecution(node_name="test")

        assert execution.node_name == "test"
        assert execution.state == NodeState.PENDING
        assert execution.start_time is None
        assert execution.end_time is None
        assert execution.error is None
        assert execution.outputs is None

    def test_custom_values(self):
        """Test custom values for NodeExecution."""
        execution = NodeExecution(
            node_name="test",
            state=NodeState.COMPLETED,
            outputs={"result": 42},
        )

        assert execution.state == NodeState.COMPLETED
        assert execution.outputs == {"result": 42}


class TestNodeState:
    """Tests for NodeState enum."""

    def test_state_values(self):
        """Test all state values exist."""
        assert NodeState.PENDING.value == "pending"
        assert NodeState.RUNNING.value == "running"
        assert NodeState.COMPLETED.value == "completed"
        assert NodeState.FAILED.value == "failed"
        assert NodeState.SKIPPED.value == "skipped"

    def test_state_is_string(self):
        """Test states are string-based."""
        assert isinstance(NodeState.PENDING, str)
        assert NodeState.PENDING == "pending"


class TestInMemoryStateTracker:
    """Tests for InMemoryStateTracker."""

    @pytest.fixture
    def tracker(self):
        """Create a test tracker."""
        return InMemoryStateTracker("test_workflow", "run_001")

    def test_initial_state(self, tracker):
        """Test initial state is pending."""
        assert tracker.get_state("any_node") == NodeState.PENDING

    def test_mark_running(self, tracker):
        """Test marking node as running."""
        tracker.mark_running("node_a")

        assert tracker.get_state("node_a") == NodeState.RUNNING
        assert tracker.executions["node_a"].start_time is not None

    def test_mark_completed(self, tracker):
        """Test marking node as completed."""
        tracker.mark_running("node_a")
        tracker.mark_completed("node_a", {"output": 42})

        assert tracker.get_state("node_a") == NodeState.COMPLETED
        assert tracker.executions["node_a"].outputs == {"output": 42}
        assert tracker.executions["node_a"].end_time is not None

    def test_mark_failed(self, tracker):
        """Test marking node as failed."""
        tracker.mark_running("node_a")
        tracker.mark_failed("node_a", "Something went wrong")

        assert tracker.get_state("node_a") == NodeState.FAILED
        assert tracker.executions["node_a"].error == "Something went wrong"

    def test_mark_skipped(self, tracker):
        """Test marking node as skipped."""
        tracker.mark_skipped("node_a")

        assert tracker.get_state("node_a") == NodeState.SKIPPED

    def test_is_completed(self, tracker):
        """Test is_completed check."""
        assert not tracker.is_completed("node_a")

        tracker.mark_running("node_a")
        assert not tracker.is_completed("node_a")

        tracker.mark_completed("node_a", {})
        assert tracker.is_completed("node_a")

    def test_get_completed_nodes(self, tracker):
        """Test getting list of completed nodes."""
        tracker.mark_completed("node_a", {})
        tracker.mark_completed("node_b", {})
        tracker.mark_failed("node_c", "error")

        completed = tracker.get_completed_nodes()
        assert set(completed) == {"node_a", "node_b"}

    def test_get_failed_nodes(self, tracker):
        """Test getting list of failed nodes."""
        tracker.mark_completed("node_a", {})
        tracker.mark_failed("node_b", "error 1")
        tracker.mark_failed("node_c", "error 2")

        failed = tracker.get_failed_nodes()
        assert set(failed) == {"node_b", "node_c"}

    def test_get_outputs(self, tracker):
        """Test getting outputs from completed node."""
        tracker.mark_completed("node_a", {"result": 123})

        assert tracker.get_outputs("node_a") == {"result": 123}
        assert tracker.get_outputs("nonexistent") is None

    def test_summary(self, tracker):
        """Test summary generation."""
        tracker.mark_completed("node_a", {})
        tracker.mark_completed("node_b", {})
        tracker.mark_failed("node_c", "error")

        summary = tracker.summary()

        assert summary["run_id"] == "run_001"
        assert summary["workflow"] == "test_workflow"
        assert summary["completed"] == 2
        assert summary["failed"] == 1
        assert summary["total"] == 3
        assert "start_time" in summary


class TestFileStateTracker:
    """Tests for FileStateTracker."""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create a test file tracker."""
        log_path = tmp_path / "state.jsonl"
        return FileStateTracker("test_workflow", "run_001", log_path)

    def test_mark_running_writes_record(self, tracker, tmp_path):
        """Test mark_running writes to file."""
        tracker.mark_running("node_a")

        log_path = tmp_path / "state.jsonl"
        assert log_path.exists()

        with log_path.open() as f:
            record = json.loads(f.readline())

        assert record["node"] == "node_a"
        assert record["state"] == "running"
        assert record["run_id"] == "run_001"
        assert record["workflow"] == "test_workflow"
        assert "timestamp" in record

    def test_mark_completed_writes_outputs(self, tracker, tmp_path):
        """Test mark_completed writes outputs."""
        tracker.mark_completed("node_a", {"result": 42})

        log_path = tmp_path / "state.jsonl"
        with log_path.open() as f:
            record = json.loads(f.readline())

        assert record["state"] == "completed"
        assert record["outputs"] == {"result": 42}

    def test_mark_failed_writes_error(self, tracker, tmp_path):
        """Test mark_failed writes error message."""
        tracker.mark_failed("node_a", "Something went wrong")

        log_path = tmp_path / "state.jsonl"
        with log_path.open() as f:
            record = json.loads(f.readline())

        assert record["state"] == "failed"
        assert record["error"] == "Something went wrong"

    def test_mark_skipped_writes_record(self, tracker, tmp_path):
        """Test mark_skipped writes record."""
        tracker.mark_skipped("node_a")

        log_path = tmp_path / "state.jsonl"
        with log_path.open() as f:
            record = json.loads(f.readline())

        assert record["state"] == "skipped"

    def test_multiple_records_appended(self, tracker, tmp_path):
        """Test multiple records are appended."""
        tracker.mark_running("node_a")
        tracker.mark_completed("node_a", {"x": 1})
        tracker.mark_running("node_b")

        log_path = tmp_path / "state.jsonl"
        with log_path.open() as f:
            lines = f.readlines()

        assert len(lines) == 3
        records = [json.loads(line) for line in lines]
        assert records[0]["state"] == "running"
        assert records[1]["state"] == "completed"
        assert records[2]["node"] == "node_b"

    def test_get_state_returns_pending_for_unknown(self, tracker):
        """Test get_state returns PENDING for unknown node."""
        assert tracker.get_state("unknown_node") == NodeState.PENDING

    def test_get_state_returns_latest_state(self, tracker, tmp_path):
        """Test get_state returns the latest state for a node."""
        tracker.mark_running("node_a")
        assert tracker.get_state("node_a") == NodeState.RUNNING

        tracker.mark_completed("node_a", {"result": 42})
        assert tracker.get_state("node_a") == NodeState.COMPLETED

    def test_is_completed_returns_true_for_completed(self, tracker):
        """Test is_completed returns True for completed node."""
        tracker.mark_completed("node_a", {})
        assert tracker.is_completed("node_a") is True

    def test_is_completed_returns_false_for_running(self, tracker):
        """Test is_completed returns False for running node."""
        tracker.mark_running("node_a")
        assert tracker.is_completed("node_a") is False

    def test_get_completed_nodes_returns_completed(self, tracker):
        """Test get_completed_nodes returns only completed nodes."""
        tracker.mark_completed("node_a", {})
        tracker.mark_completed("node_b", {})
        tracker.mark_failed("node_c", "error")

        completed = tracker.get_completed_nodes()
        assert set(completed) == {"node_a", "node_b"}

    def test_get_failed_nodes_returns_failed(self, tracker):
        """Test get_failed_nodes returns only failed nodes."""
        tracker.mark_completed("node_a", {})
        tracker.mark_failed("node_b", "error1")
        tracker.mark_failed("node_c", "error2")

        failed = tracker.get_failed_nodes()
        assert set(failed) == {"node_b", "node_c"}

    def test_creates_parent_directory(self, tmp_path):
        """Test creates parent directory if needed."""
        log_path = tmp_path / "subdir" / "nested" / "state.jsonl"
        tracker = FileStateTracker("test", "run", log_path)

        tracker.mark_running("node")
        assert log_path.exists()

    def test_filters_by_run_id(self, tmp_path):
        """Test that queries filter by run_id."""
        log_path = tmp_path / "state.jsonl"

        # Two trackers with different run_ids sharing the same file
        tracker1 = FileStateTracker("wf", "run_001", log_path)
        tracker2 = FileStateTracker("wf", "run_002", log_path)

        tracker1.mark_completed("node_a", {})
        tracker2.mark_completed("node_b", {})

        # Each tracker should only see its own completed nodes
        assert tracker1.get_completed_nodes() == ["node_a"]
        assert tracker2.get_completed_nodes() == ["node_b"]
