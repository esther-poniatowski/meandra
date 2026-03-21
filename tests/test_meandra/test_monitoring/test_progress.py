"""
test_meandra.test_monitoring.test_progress
==========================================

Tests for meandra.monitoring.progress module.
"""

import pytest
import time

from meandra.monitoring.progress import (
    ProgressTracker,
    NodeProgress,
    NodeStatus,
)


class TestNodeStatus:
    """Tests for NodeStatus enum."""

    def test_status_values(self):
        """Test that all expected statuses exist."""
        assert NodeStatus.PENDING.value == "pending"
        assert NodeStatus.RUNNING.value == "running"
        assert NodeStatus.COMPLETED.value == "completed"
        assert NodeStatus.FAILED.value == "failed"
        assert NodeStatus.SKIPPED.value == "skipped"


class TestNodeProgress:
    """Tests for NodeProgress dataclass."""

    def test_default_values(self):
        """Test default node progress values."""
        progress = NodeProgress(name="test_node")
        assert progress.name == "test_node"
        assert progress.status == NodeStatus.PENDING
        assert progress.start_time is None
        assert progress.end_time is None
        assert progress.error is None

    def test_duration_not_started(self):
        """Test duration when not started."""
        progress = NodeProgress(name="test")
        assert progress.duration_seconds is None

    def test_duration_running(self):
        """Test duration while running."""
        progress = NodeProgress(
            name="test",
            status=NodeStatus.RUNNING,
            start_time=time.time() - 1.0,
        )
        duration = progress.duration_seconds
        assert duration is not None
        assert duration >= 1.0

    def test_duration_completed(self):
        """Test duration when completed."""
        start = time.time() - 5.0
        end = time.time() - 2.0
        progress = NodeProgress(
            name="test",
            status=NodeStatus.COMPLETED,
            start_time=start,
            end_time=end,
        )
        assert progress.duration_seconds == pytest.approx(3.0, abs=0.1)


class TestProgressTracker:
    """Tests for ProgressTracker."""

    def test_initial_state(self):
        """Test initial tracker state."""
        tracker = ProgressTracker("workflow", total_nodes=5)
        assert tracker.workflow_name == "workflow"
        assert tracker.total_nodes == 5
        assert tracker.completed_count == 0
        assert tracker.failed_count == 0
        assert tracker.running_count == 0
        assert tracker.percentage == 0.0
        assert not tracker.is_complete

    def test_start_node(self):
        """Test starting a node."""
        tracker = ProgressTracker("wf", total_nodes=3)
        tracker.start_node("node1")

        assert "node1" in tracker.nodes
        assert tracker.nodes["node1"].status == NodeStatus.RUNNING
        assert tracker.nodes["node1"].start_time is not None
        assert tracker.running_count == 1

    def test_complete_node(self):
        """Test completing a node."""
        tracker = ProgressTracker("wf", total_nodes=3)
        tracker.start_node("node1")
        tracker.complete_node("node1", {"result": "data"})

        assert tracker.nodes["node1"].status == NodeStatus.COMPLETED
        assert tracker.nodes["node1"].end_time is not None
        assert tracker.completed_count == 1
        assert tracker.running_count == 0
        assert tracker.percentage == pytest.approx(33.33, abs=1)

    def test_fail_node(self):
        """Test failing a node."""
        tracker = ProgressTracker("wf", total_nodes=3)
        tracker.start_node("node1")
        tracker.fail_node("node1", "Something went wrong")

        assert tracker.nodes["node1"].status == NodeStatus.FAILED
        assert tracker.nodes["node1"].error == "Something went wrong"
        assert tracker.failed_count == 1

    def test_skip_node(self):
        """Test skipping a node."""
        tracker = ProgressTracker("wf", total_nodes=3)
        tracker.skip_node("node1")

        assert tracker.nodes["node1"].status == NodeStatus.SKIPPED
        assert tracker.completed_count == 1  # Skipped counts as processed

    def test_is_complete(self):
        """Test completion detection."""
        tracker = ProgressTracker("wf", total_nodes=2)
        assert not tracker.is_complete

        tracker.complete_node("node1")
        assert not tracker.is_complete

        tracker.complete_node("node2")
        assert tracker.is_complete

    def test_is_complete_with_failures(self):
        """Test completion with failures."""
        tracker = ProgressTracker("wf", total_nodes=2)
        tracker.complete_node("node1")
        tracker.fail_node("node2", "error")
        assert tracker.is_complete

    def test_percentage_empty_workflow(self):
        """Test percentage with zero nodes."""
        tracker = ProgressTracker("wf", total_nodes=0)
        assert tracker.percentage == 100.0

    def test_callback_notification(self):
        """Test that callbacks are notified."""
        notifications = []

        def callback(tracker):
            notifications.append(tracker.percentage)

        tracker = ProgressTracker("wf", total_nodes=2)
        tracker.add_callback(callback)

        tracker.complete_node("node1")
        tracker.complete_node("node2")

        assert len(notifications) == 2
        assert notifications[0] == pytest.approx(50.0, abs=1)
        assert notifications[1] == pytest.approx(100.0, abs=1)

    def test_remove_callback(self):
        """Test removing a callback."""
        notifications = []

        def callback(tracker):
            notifications.append(1)

        tracker = ProgressTracker("wf", total_nodes=2)
        tracker.add_callback(callback)
        tracker.complete_node("node1")  # Callback fires
        tracker.remove_callback(callback)
        tracker.complete_node("node2")  # Callback should not fire

        assert len(notifications) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        tracker = ProgressTracker("wf", total_nodes=3)
        tracker.start_node("node1")
        tracker.complete_node("node1")
        tracker.fail_node("node2", "error")

        result = tracker.to_dict()

        assert result["workflow_name"] == "wf"
        assert result["total_nodes"] == 3
        assert result["completed"] == 1
        assert result["failed"] == 1
        assert "nodes" in result
        assert result["nodes"]["node1"]["status"] == "completed"
        assert result["nodes"]["node2"]["status"] == "failed"
        assert result["nodes"]["node2"]["error"] == "error"

    def test_summary(self):
        """Test summary string."""
        tracker = ProgressTracker("my_workflow", total_nodes=4)
        tracker.complete_node("node1")
        tracker.complete_node("node2")

        summary = tracker.summary()

        assert "my_workflow" in summary
        assert "50%" in summary
        assert "2/4" in summary

    def test_finish(self):
        """Test finishing the workflow."""
        tracker = ProgressTracker("wf", total_nodes=2)
        tracker.complete_node("node1")
        tracker.complete_node("node2")
        tracker.finish()

        assert tracker.end_time is not None
        assert tracker.is_complete

    def test_elapsed_seconds(self):
        """Test elapsed time calculation."""
        tracker = ProgressTracker("wf", total_nodes=1)
        time.sleep(0.1)
        elapsed = tracker.elapsed_seconds
        assert elapsed >= 0.1


class TestProgressTrackerIntegration:
    """Integration tests for ProgressTracker."""

    def test_full_workflow_execution(self):
        """Test tracking a complete workflow execution."""
        tracker = ProgressTracker("integration_test", total_nodes=3)

        # Simulate workflow execution
        tracker.start_node("load")
        time.sleep(0.01)
        tracker.complete_node("load", {"data": [1, 2, 3]})

        tracker.start_node("process")
        time.sleep(0.01)
        tracker.complete_node("process", {"result": 6})

        tracker.start_node("save")
        time.sleep(0.01)
        tracker.complete_node("save", {"path": "out.pkl"})

        tracker.finish()

        assert tracker.completed_count == 3
        assert tracker.failed_count == 0
        assert tracker.percentage == 100.0
        assert tracker.is_complete
        assert tracker.elapsed_seconds > 0


if __name__ == "__main__":
    pytest.main()
