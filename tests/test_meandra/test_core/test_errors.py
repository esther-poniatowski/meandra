"""
test_meandra.test_core.test_errors
==================================

Tests for meandra.core.errors module.
"""

import pytest

from meandra.core.errors import (
    MeandraError,
    WorkflowError,
    NodeExecutionError,
    DependencyResolutionError,
    ValidationError,
    CheckpointError,
    TimeoutError,
    ConfigurationError,
    RetryExhaustedError,
)


class TestMeandraError:
    """Tests for MeandraError base class."""

    def test_basic_error(self):
        """Test creating a basic error."""
        error = MeandraError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}

    def test_error_with_details(self):
        """Test creating an error with details."""
        error = MeandraError("Failed", code=42, context="test")
        assert "code=42" in str(error)
        assert "context='test'" in str(error)
        assert error.details == {"code": 42, "context": "test"}

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = MeandraError("Test error", extra="value")
        result = error.to_dict()
        assert result["type"] == "MeandraError"
        assert result["message"] == "Test error"
        assert result["extra"] == "value"


class TestWorkflowError:
    """Tests for WorkflowError."""

    def test_workflow_error(self):
        """Test creating a workflow error."""
        error = WorkflowError("Workflow failed", workflow_name="my_workflow")
        assert error.workflow_name == "my_workflow"
        assert "workflow_name='my_workflow'" in str(error)

    def test_workflow_error_to_dict(self):
        """Test workflow error serialization."""
        error = WorkflowError("Failed", workflow_name="test_wf")
        result = error.to_dict()
        assert result["workflow_name"] == "test_wf"


class TestNodeExecutionError:
    """Tests for NodeExecutionError."""

    def test_node_execution_error(self):
        """Test creating a node execution error."""
        original = ValueError("Bad value")
        error = NodeExecutionError(
            "Node failed",
            workflow_name="wf",
            node_name="processor",
            original_error=original,
        )
        assert error.workflow_name == "wf"
        assert error.node_name == "processor"
        assert error.original_error is original

    def test_node_execution_error_to_dict(self):
        """Test node execution error serialization."""
        original = TypeError("Wrong type")
        error = NodeExecutionError(
            "Failed",
            workflow_name="wf",
            node_name="node1",
            original_error=original,
        )
        result = error.to_dict()
        assert result["node_name"] == "node1"
        assert result["original_error"]["type"] == "TypeError"
        assert "Wrong type" in result["original_error"]["message"]


class TestDependencyResolutionError:
    """Tests for DependencyResolutionError."""

    def test_with_cycle(self):
        """Test error with cycle information."""
        error = DependencyResolutionError(
            "Cycle detected",
            workflow_name="wf",
            cycle=["a", "b", "c"],
        )
        assert error.cycle == ["a", "b", "c"]
        result = error.to_dict()
        assert result["cycle"] == ["a", "b", "c"]

    def test_with_missing(self):
        """Test error with missing dependencies."""
        error = DependencyResolutionError(
            "Missing dependencies",
            workflow_name="wf",
            missing=["dep1", "dep2"],
        )
        assert error.missing == ["dep1", "dep2"]


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_with_errors(self):
        """Test validation error with error list."""
        error = ValidationError(
            "Validation failed",
            workflow_name="wf",
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        assert len(error.errors) == 2
        assert len(error.warnings) == 1
        result = error.to_dict()
        assert result["errors"] == ["Error 1", "Error 2"]
        assert result["warnings"] == ["Warning 1"]


class TestCheckpointError:
    """Tests for CheckpointError."""

    def test_checkpoint_error(self):
        """Test checkpoint error."""
        error = CheckpointError(
            "Failed to save checkpoint",
            operation="save",
            checkpoint_id="ckpt-123",
        )
        assert error.operation == "save"
        assert error.checkpoint_id == "ckpt-123"


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_timeout_error(self):
        """Test timeout error."""
        error = TimeoutError(
            "Operation timed out",
            timeout_seconds=30.0,
            operation="node_execution",
            elapsed_seconds=32.5,
        )
        assert error.timeout_seconds == 30.0
        assert error.elapsed_seconds == 32.5
        assert error.operation == "node_execution"


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error(self):
        """Test configuration error."""
        error = ConfigurationError(
            "Invalid configuration",
            config_key="database.host",
        )
        assert error.config_key == "database.host"


class TestRetryExhaustedError:
    """Tests for RetryExhaustedError."""

    def test_retry_exhausted_error(self):
        """Test retry exhausted error."""
        last = ConnectionError("Connection refused")
        error = RetryExhaustedError(
            "All attempts failed",
            attempts=3,
            last_error=last,
        )
        assert error.attempts == 3
        assert error.last_error is last

    def test_retry_exhausted_to_dict(self):
        """Test retry exhausted serialization."""
        last = ValueError("Bad")
        error = RetryExhaustedError("Failed", attempts=5, last_error=last)
        result = error.to_dict()
        assert result["attempts"] == 5
        assert result["last_error"]["type"] == "ValueError"


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_all_inherit_from_meandra_error(self):
        """Test that all errors inherit from MeandraError."""
        assert issubclass(WorkflowError, MeandraError)
        assert issubclass(NodeExecutionError, MeandraError)
        assert issubclass(DependencyResolutionError, MeandraError)
        assert issubclass(ValidationError, MeandraError)
        assert issubclass(CheckpointError, MeandraError)
        assert issubclass(TimeoutError, MeandraError)
        assert issubclass(ConfigurationError, MeandraError)
        assert issubclass(RetryExhaustedError, MeandraError)

    def test_workflow_errors_inherit_from_workflow_error(self):
        """Test that workflow-related errors inherit properly."""
        assert issubclass(NodeExecutionError, WorkflowError)
        assert issubclass(DependencyResolutionError, WorkflowError)
        assert issubclass(ValidationError, WorkflowError)

    def test_can_catch_base_exception(self):
        """Test that all errors can be caught with MeandraError."""
        errors = [
            MeandraError("test"),
            WorkflowError("test", workflow_name="wf"),
            NodeExecutionError("test", workflow_name="wf", node_name="n"),
            CheckpointError("test", operation="save"),
        ]
        for error in errors:
            try:
                raise error
            except MeandraError as e:
                assert e is error


if __name__ == "__main__":
    pytest.main()
