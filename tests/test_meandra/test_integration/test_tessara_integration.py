"""
test_meandra.test_integration.test_tessara_integration
======================================================

Tests for Tessara integration adapters.
"""

import pytest
from unittest.mock import MagicMock, patch

from meandra.core.node import Node
from meandra.core.workflow import Workflow
from meandra.integration.tessara import TessaraNodeAdapter, SweepOrchestrator


# --- Mock Tessara classes for testing without dependency ---

class MockParam:
    """Mock Tessara Param for testing."""

    def __init__(self, default=None, value=None):
        self._default = default
        self._value = value

    def get(self):
        return self._value if self._value is not None else self._default

    def set(self, value):
        self._value = value
        return self

    def validate_value(self, value):
        if value is None:
            raise ValueError("Invalid value")


class MockParameterSet:
    """Mock Tessara ParameterSet for testing."""

    def __init__(self, **kwargs):
        self.data = {}
        for name, param in kwargs.items():
            if isinstance(param, MockParam):
                self.data[name] = param
            elif isinstance(param, MockParameterSet):
                self.data[name] = param
            else:
                self.data[name] = MockParam(default=param)

    def get(self, name):
        return self.data[name].get()

    def get_value(self, name):
        if "." in name:
            parts = name.split(".")
            obj = self
            for part in parts[:-1]:
                obj = obj.data[part]
            return obj.data[parts[-1]].get()
        return self.get(name)

    def to_dict(self, values_only=False):
        if values_only:
            result = {}
            for name, param in self.data.items():
                if isinstance(param, MockParameterSet):
                    result[name] = param.to_dict(values_only=True)
                else:
                    result[name] = param.get()
            return result
        return {name: {"value": param._value, "default": param._default} for name, param in self.data.items()}

    def keys(self):
        return self.data.keys()


class MockParamSweeper:
    """Mock Tessara ParamSweeper for testing."""

    def __init__(self, combinations):
        self._combinations = combinations

    def __iter__(self):
        return iter(self._combinations)

    def __len__(self):
        return len(self._combinations)


# --- Tests for TessaraNodeAdapter ---


class TestTessaraNodeAdapter:
    """Tests for TessaraNodeAdapter."""

    def test_get_param_values_all(self):
        """Test getting all parameter values."""
        params = MockParameterSet(lr=0.01, epochs=100, batch_size=32)
        adapter = TessaraNodeAdapter(params)

        values = adapter.get_param_values()

        assert values == {"lr": 0.01, "epochs": 100, "batch_size": 32}

    def test_get_param_values_subset(self):
        """Test getting specific parameter values."""
        params = MockParameterSet(lr=0.01, epochs=100, batch_size=32)
        adapter = TessaraNodeAdapter(params)

        values = adapter.get_param_values(names=["lr", "epochs"])

        assert values == {"lr": 0.01, "epochs": 100}
        assert "batch_size" not in values

    def test_wrap_function_injects_params(self):
        """Test that wrapped function receives injected parameters."""
        params = MockParameterSet(threshold=0.5, multiplier=2)
        adapter = TessaraNodeAdapter(params)

        def process(inputs, threshold, multiplier):
            return {"result": [x * multiplier for x in inputs["data"] if x > threshold]}

        wrapped = adapter.wrap_function(process)
        result = wrapped({"data": [0.3, 0.6, 0.8]})

        assert result == {"result": [1.2, 1.6]}

    def test_wrap_function_auto_discovers_params(self):
        """Test that wrap_function auto-discovers matching parameters."""
        params = MockParameterSet(a=10, b=20, c=30)
        adapter = TessaraNodeAdapter(params)

        def func(inputs, a, b):
            return {"sum": a + b}

        wrapped = adapter.wrap_function(func)
        result = wrapped({})

        assert result == {"sum": 30}

    def test_wrap_function_uses_aliases(self):
        """Test alias mapping for dotted parameter names."""
        params = MockParameterSet(model=MockParameterSet(lr=0.1))
        adapter = TessaraNodeAdapter(params)

        def func(inputs, model_lr):
            return {"lr": model_lr}

        wrapped = adapter.wrap_function(
            func,
            param_aliases={"model.lr": "model_lr"},
        )
        result = wrapped({})

        assert result == {"lr": 0.1}

    def test_wrap_function_discovers_nested_params(self):
        """Test auto-discovery with nested parameters using dotted paths."""
        params = MockParameterSet(model=MockParameterSet(lr=0.1))
        adapter = TessaraNodeAdapter(params)

        def func(inputs, **kwargs):
            return {"lr": kwargs["model.lr"]}

        wrapped = adapter.wrap_function(func)
        result = wrapped({})

        assert result == {"lr": 0.1}

    def test_wrap_function_explicit_param_names(self):
        """Test specifying explicit parameter names."""
        params = MockParameterSet(a=10, b=20, c=30)
        adapter = TessaraNodeAdapter(params)

        def func(inputs, a):
            return {"value": a}

        wrapped = adapter.wrap_function(func, param_names=["a"])
        result = wrapped({})

        assert result == {"value": 10}

    def test_bind_to_node_creates_new_node(self):
        """Test that bind_to_node returns a new node with wrapped function."""
        params = MockParameterSet(factor=2)
        adapter = TessaraNodeAdapter(params)

        def multiply(inputs, factor):
            return {"result": inputs["value"] * factor}

        original_node = Node(
            name="multiplier",
            func=multiply,
            inputs=["value"],
            outputs=["result"],
        )

        adapted_node = adapter.bind_to_node(original_node)

        assert adapted_node.name == "multiplier"
        assert adapted_node.inputs == ["value"]
        assert adapted_node.outputs == ["result"]

        # Test the adapted function works
        result = adapted_node.execute({"value": 5})
        assert result == {"result": 10}

    def test_adapt_workflow_adapts_all_nodes(self):
        """Test that adapt_workflow adapts all nodes by default."""
        params = MockParameterSet(scale=10)
        adapter = TessaraNodeAdapter(params)

        def node1_func(inputs, scale):
            return {"a": scale}

        def node2_func(inputs, scale):
            return {"b": inputs["a"] + scale}

        workflow = Workflow("test")
        workflow.add_node(Node("node1", node1_func, outputs=["a"]))
        workflow.add_node(Node("node2", node2_func, dependencies=["node1"], inputs=["a"], outputs=["b"]))

        adapted = adapter.adapt_workflow(workflow)

        assert len(adapted.nodes) == 2
        assert "node1" in adapted.nodes
        assert "node2" in adapted.nodes


class TestSweepOrchestrator:
    """Tests for SweepOrchestrator."""

    def test_run_sweep_executes_all_combinations(self):
        """Test that run_sweep executes for all parameter combinations."""
        # Create mock combinations
        combo1 = MockParameterSet(lr=0.01)
        combo2 = MockParameterSet(lr=0.001)
        sweeper = MockParamSweeper([combo1, combo2])

        # Create mock orchestrator
        mock_orch = MagicMock()
        mock_orch.run.return_value = {"output": "result"}

        sweep_orch = SweepOrchestrator(mock_orch, sweeper)

        # Create simple workflow
        workflow = Workflow("test")
        workflow.add_node(Node("dummy", lambda inputs: inputs, outputs=["out"]))

        results = sweep_orch.run_sweep(workflow)

        assert len(results) == 2
        assert mock_orch.run.call_count == 2

    def test_run_sweep_collects_results(self):
        """Test that run_sweep collects results from all runs."""
        combo1 = MockParameterSet(lr=0.01)
        combo2 = MockParameterSet(lr=0.001)
        sweeper = MockParamSweeper([combo1, combo2])

        mock_orch = MagicMock()
        mock_orch.run.side_effect = [
            {"loss": 0.5},
            {"loss": 0.3},
        ]

        sweep_orch = SweepOrchestrator(mock_orch, sweeper)
        workflow = Workflow("test")
        workflow.add_node(Node("dummy", lambda inputs: inputs, outputs=["out"]))

        results = sweep_orch.run_sweep(workflow)

        assert results[0]["outputs"] == {"loss": 0.5}
        assert results[0]["success"] is True
        assert results[1]["outputs"] == {"loss": 0.3}
        assert results[1]["success"] is True

    def test_run_sweep_uses_input_copy(self):
        """Test that inputs are copied per run."""
        combo1 = MockParameterSet(lr=0.01)
        combo2 = MockParameterSet(lr=0.001)
        sweeper = MockParamSweeper([combo1, combo2])

        def mutating_node(inputs):
            inputs["mutated"] = True
            return {"ok": True}

        workflow = Workflow("test")
        workflow.add_node(Node("mutate", mutating_node, outputs=["ok"]))

        mock_orch = MagicMock()
        mock_orch.run.side_effect = lambda wf, inputs: {"mutated": "mutated" in inputs}

        sweep_orch = SweepOrchestrator(mock_orch, sweeper)

        base_inputs = {"seed": 1}
        results = sweep_orch.run_sweep(workflow, inputs=base_inputs)

        assert results[0]["outputs"]["mutated"] is False
        assert results[1]["outputs"]["mutated"] is False

    def test_run_sweep_handles_errors(self):
        """Test that run_sweep handles errors gracefully."""
        combo1 = MockParameterSet(lr=0.01)
        combo2 = MockParameterSet(lr=0.001)
        sweeper = MockParamSweeper([combo1, combo2])

        mock_orch = MagicMock()
        mock_orch.run.side_effect = [
            {"loss": 0.5},
            RuntimeError("Training failed"),
        ]

        sweep_orch = SweepOrchestrator(mock_orch, sweeper)
        workflow = Workflow("test")
        workflow.add_node(Node("dummy", lambda inputs: inputs, outputs=["out"]))

        results = sweep_orch.run_sweep(workflow)

        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "Training failed" in results[1]["error"]

    def test_run_sweep_calls_callback(self):
        """Test that run_sweep calls the on_run_complete callback."""
        combo1 = MockParameterSet(lr=0.01)
        sweeper = MockParamSweeper([combo1])

        mock_orch = MagicMock()
        mock_orch.run.return_value = {"result": 1}

        callback = MagicMock()

        sweep_orch = SweepOrchestrator(mock_orch, sweeper)
        workflow = Workflow("test")
        workflow.add_node(Node("dummy", lambda inputs: inputs, outputs=["out"]))

        sweep_orch.run_sweep(workflow, on_run_complete=callback)

        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0] == 0  # index
        assert args[1] == {"lr": 0.01}  # params dict

    def test_len_returns_combination_count(self):
        """Test __len__ returns correct count."""
        sweeper = MockParamSweeper([1, 2, 3, 4, 5])
        sweep_orch = SweepOrchestrator(MagicMock(), sweeper)

        assert len(sweep_orch) == 5


if __name__ == "__main__":
    pytest.main()
