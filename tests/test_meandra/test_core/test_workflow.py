"""
Tests for core workflow functionality.
"""

import pytest

from meandra import (
    Node,
    Workflow,
    DAGScheduler,
    DependencyResolutionError,
    ValidationResult,
    ValidationError,
)


class TestNode:
    """Tests for Node class."""

    def test_node_creation(self):
        """Test basic node creation."""
        def my_func(inputs):
            return {"output": inputs["input"] * 2}

        node = Node("test_node", my_func, inputs=["input"], outputs=["output"])

        assert node.name == "test_node"
        assert node.inputs == ["input"]
        assert node.outputs == ["output"]
        assert node.dependencies == []

    def test_node_execution(self):
        """Test node execution returns dict."""
        def add(inputs):
            return {"sum": inputs["a"] + inputs["b"]}

        node = Node("adder", add, inputs=["a", "b"], outputs=["sum"])
        result = node.execute({"a": 1, "b": 2})

        assert result == {"sum": 3}

    def test_node_execution_wraps_single_output(self):
        """Test that single value outputs are wrapped in dict."""
        def double(inputs):
            return inputs["x"] * 2

        node = Node("doubler", double, inputs=["x"], outputs=["result"])
        result = node.execute({"x": 5})

        assert result == {"result": 10}

    def test_node_hash_and_equality(self):
        """Test node hashing and equality based on name."""
        node1 = Node("test", lambda x: x)
        node2 = Node("test", lambda x: x * 2)
        node3 = Node("other", lambda x: x)

        assert node1 == node2
        assert node1 != node3
        assert hash(node1) == hash(node2)


class TestWorkflow:
    """Tests for Workflow class."""

    def test_workflow_creation(self):
        """Test basic workflow creation."""
        wf = Workflow("test_workflow")
        assert wf.name == "test_workflow"
        assert len(wf) == 0

    def test_add_node(self):
        """Test adding nodes to workflow."""
        wf = Workflow("test")
        node = Node("node1", lambda x: x)
        wf.add_node(node)

        assert len(wf) == 1
        assert "node1" in wf

    def test_add_duplicate_node_raises(self):
        """Test that adding duplicate node name raises."""
        wf = Workflow("test")
        wf.add_node(Node("node1", lambda x: x))

        with pytest.raises(ValueError, match="already exists"):
            wf.add_node(Node("node1", lambda x: x * 2))

    def test_get_node(self):
        """Test retrieving node by name."""
        wf = Workflow("test")
        node = Node("node1", lambda x: x)
        wf.add_node(node)

        retrieved = wf.get_node("node1")
        assert retrieved is node

    def test_get_nonexistent_node_raises(self):
        """Test that getting nonexistent node raises."""
        wf = Workflow("test")

        with pytest.raises(KeyError, match="not found"):
            wf.get_node("nonexistent")

    def test_workflow_iteration(self):
        """Test iterating over workflow nodes."""
        wf = Workflow("test")
        wf.add_node(Node("node1", lambda x: x))
        wf.add_node(Node("node2", lambda x: x))

        names = [node.name for node in wf]
        assert set(names) == {"node1", "node2"}


class TestDAGScheduler:
    """Tests for DAGScheduler."""

    def test_empty_workflow(self):
        """Test scheduling empty workflow."""
        scheduler = DAGScheduler()
        wf = Workflow("empty")

        layers = scheduler.resolve(wf)
        assert layers == []

    def test_single_node(self):
        """Test scheduling single node."""
        scheduler = DAGScheduler()
        wf = Workflow("single")
        wf.add_node(Node("node1", lambda x: x))

        layers = scheduler.resolve(wf)
        assert len(layers) == 1
        assert len(layers[0]) == 1
        assert layers[0][0].name == "node1"

    def test_independent_nodes_same_layer(self):
        """Test that independent nodes are in same layer."""
        scheduler = DAGScheduler()
        wf = Workflow("parallel")
        wf.add_node(Node("node1", lambda x: x))
        wf.add_node(Node("node2", lambda x: x))
        wf.add_node(Node("node3", lambda x: x))

        layers = scheduler.resolve(wf)
        assert len(layers) == 1
        assert len(layers[0]) == 3

    def test_linear_dependencies(self):
        """Test linear dependency chain."""
        scheduler = DAGScheduler()
        wf = Workflow("linear")
        wf.add_node(Node("node1", lambda x: x))
        wf.add_node(Node("node2", lambda x: x, dependencies=["node1"]))
        wf.add_node(Node("node3", lambda x: x, dependencies=["node2"]))

        layers = scheduler.resolve(wf)
        assert len(layers) == 3
        assert layers[0][0].name == "node1"
        assert layers[1][0].name == "node2"
        assert layers[2][0].name == "node3"

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency graph."""
        scheduler = DAGScheduler()
        wf = Workflow("diamond")

        # A -> B, C -> D (diamond shape)
        wf.add_node(Node("A", lambda x: x))
        wf.add_node(Node("B", lambda x: x, dependencies=["A"]))
        wf.add_node(Node("C", lambda x: x, dependencies=["A"]))
        wf.add_node(Node("D", lambda x: x, dependencies=["B", "C"]))

        layers = scheduler.resolve(wf)

        assert len(layers) == 3
        assert layers[0][0].name == "A"
        assert set(n.name for n in layers[1]) == {"B", "C"}
        assert layers[2][0].name == "D"

    def test_cyclic_dependency_raises(self):
        """Test that cyclic dependencies are detected."""
        scheduler = DAGScheduler()
        wf = Workflow("cyclic")
        wf.add_node(Node("A", lambda x: x, dependencies=["C"]))
        wf.add_node(Node("B", lambda x: x, dependencies=["A"]))
        wf.add_node(Node("C", lambda x: x, dependencies=["B"]))

        with pytest.raises(DependencyResolutionError, match="circular dependencies"):
            scheduler.resolve(wf)

    def test_missing_dependency_raises(self):
        """Test that missing dependency is caught."""
        scheduler = DAGScheduler()
        wf = Workflow("missing")
        wf.add_node(Node("node1", lambda x: x, dependencies=["nonexistent"]))

        with pytest.raises(KeyError, match="does not exist"):
            scheduler.resolve(wf)

    def test_get_execution_order(self):
        """Test flat execution order."""
        scheduler = DAGScheduler()
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x))
        wf.add_node(Node("B", lambda x: x, dependencies=["A"]))

        order = scheduler.get_execution_order(wf)
        assert len(order) == 2
        assert order[0].name == "A"
        assert order[1].name == "B"


class TestWorkflowModel:
    """Tests for WorkflowModel.build_model()."""

    def test_build_model_empty_workflow(self):
        """Test building model from empty workflow."""
        from meandra import WorkflowModel

        wf = Workflow("empty")
        model = wf.build_model()

        assert isinstance(model, WorkflowModel)
        assert model.name == "empty"
        assert model.nodes == []
        assert model.edges == []
        assert model.inputs == []
        assert model.outputs == []

    def test_build_model_single_node(self):
        """Test building model from single node workflow."""
        wf = Workflow("single")
        wf.add_node(Node("loader", lambda x: x, outputs=["data"]))

        model = wf.build_model()

        assert model.name == "single"
        assert len(model.nodes) == 1
        assert model.nodes[0].name == "loader"
        assert model.edges == []
        assert model.inputs == []
        assert model.outputs == ["data"]

    def test_build_model_with_dependencies(self):
        """Test building model captures dependency edges."""
        wf = Workflow("pipeline")
        wf.add_node(Node("load", lambda x: x, outputs=["raw"]))
        wf.add_node(Node("transform", lambda x: x, dependencies=["load"], inputs=["raw"], outputs=["processed"]))
        wf.add_node(Node("save", lambda x: x, dependencies=["transform"], inputs=["processed"]))

        model = wf.build_model()

        assert len(model.nodes) == 3
        assert ("load", "transform") in model.edges
        assert ("transform", "save") in model.edges
        assert len(model.edges) == 2

    def test_build_model_collects_inputs_outputs(self):
        """Test model collects all unique inputs and outputs."""
        wf = Workflow("test")
        wf.add_node(Node("n1", lambda x: x, inputs=["a", "b"], outputs=["x"]))
        wf.add_node(Node("n2", lambda x: x, inputs=["b", "c"], outputs=["y", "z"]))

        model = wf.build_model()

        assert set(model.inputs) == {"a", "b", "c"}
        assert set(model.outputs) == {"x", "y", "z"}
        # Sorted order
        assert model.inputs == ["a", "b", "c"]
        assert model.outputs == ["x", "y", "z"]

    def test_build_model_diamond(self):
        """Test building model from diamond dependency graph."""
        wf = Workflow("diamond")
        wf.add_node(Node("A", lambda x: x, outputs=["out_a"]))
        wf.add_node(Node("B", lambda x: x, dependencies=["A"], inputs=["out_a"], outputs=["out_b"]))
        wf.add_node(Node("C", lambda x: x, dependencies=["A"], inputs=["out_a"], outputs=["out_c"]))
        wf.add_node(Node("D", lambda x: x, dependencies=["B", "C"], inputs=["out_b", "out_c"], outputs=["final"]))

        model = wf.build_model()

        assert len(model.nodes) == 4
        assert ("A", "B") in model.edges
        assert ("A", "C") in model.edges
        assert ("B", "D") in model.edges
        assert ("C", "D") in model.edges
        assert len(model.edges) == 4

    def test_workflow_model_is_immutable(self):
        """Test WorkflowModel is frozen (immutable)."""
        from dataclasses import FrozenInstanceError

        wf = Workflow("test")
        wf.add_node(Node("n1", lambda x: x))
        model = wf.build_model()

        with pytest.raises(FrozenInstanceError):
            model.name = "changed"


class TestWorkflowValidation:
    """Tests for Workflow.validate()."""

    def test_valid_workflow(self):
        """Test validation of a valid workflow."""
        wf = Workflow("test")
        wf.add_node(Node("load", lambda x: x, outputs=["data"]))
        wf.add_node(Node("process", lambda x: x, dependencies=["load"], inputs=["data"], outputs=["result"]))

        result = wf.validate()

        assert result.valid is True
        assert result.errors == []

    def test_empty_workflow_is_valid(self):
        """Test that empty workflow is valid."""
        wf = Workflow("empty")
        result = wf.validate()

        assert result.valid is True

    def test_missing_dependency(self):
        """Test detection of missing dependencies."""
        wf = Workflow("test")
        wf.add_node(Node("process", lambda x: x, dependencies=["nonexistent"]))

        result = wf.validate()

        assert result.valid is False
        assert len(result.errors) == 1
        assert "nonexistent" in result.errors[0]
        assert "does not exist" in result.errors[0]

    def test_cyclic_dependency(self):
        """Test detection of cyclic dependencies."""
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x, dependencies=["C"]))
        wf.add_node(Node("B", lambda x: x, dependencies=["A"]))
        wf.add_node(Node("C", lambda x: x, dependencies=["B"]))

        result = wf.validate()

        assert result.valid is False
        assert len(result.errors) == 1
        assert "Cyclic dependency" in result.errors[0]

    def test_self_dependency(self):
        """Test detection of self-referential dependency."""
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x, dependencies=["A"]))

        result = wf.validate()

        assert result.valid is False
        assert "Cyclic dependency" in result.errors[0]

    def test_unsatisfiable_input(self):
        """Test detection of unsatisfiable inputs."""
        wf = Workflow("test")
        wf.add_node(Node("process", lambda x: x, inputs=["missing_input"]))

        result = wf.validate(available_inputs=set())

        assert result.valid is False
        assert "missing_input" in result.errors[0]

    def test_input_satisfied_by_dependency(self):
        """Test that inputs from dependencies are valid."""
        wf = Workflow("test")
        wf.add_node(Node("load", lambda x: x, outputs=["data"]))
        wf.add_node(Node("process", lambda x: x, dependencies=["load"], inputs=["data"]))

        result = wf.validate(available_inputs=set())

        assert result.valid is True

    def test_input_satisfied_by_available_inputs(self):
        """Test that provided inputs satisfy requirements."""
        wf = Workflow("test")
        wf.add_node(Node("process", lambda x: x, inputs=["external_data"]))

        result = wf.validate(available_inputs={"external_data"})

        assert result.valid is True

    def test_warning_for_no_outputs(self):
        """Test warning for nodes with no outputs and dependents."""
        wf = Workflow("test")
        wf.add_node(Node("load", lambda x: x, outputs=["data"]))
        wf.add_node(Node("middle", lambda x: x, dependencies=["load"], inputs=["data"]))  # No outputs
        wf.add_node(Node("final", lambda x: x, dependencies=["middle"], inputs=["data"], outputs=["result"]))

        result = wf.validate()

        assert result.valid is True
        assert len(result.warnings) == 1
        assert "no outputs" in result.warnings[0]

    def test_input_requires_declared_dependency(self):
        """Test inputs must come from declared dependencies or available inputs."""
        wf = Workflow("test")
        wf.add_node(Node("a", lambda x: x, outputs=["from_a"]))
        wf.add_node(Node("c", lambda x: x, outputs=["from_c"]))
        wf.add_node(
            Node("b", lambda x: x, dependencies=["a"], inputs=["from_c"], outputs=["out"])
        )

        result = wf.validate(available_inputs=set())

        assert result.valid is False
        assert "from_c" in result.errors[0]

    def test_multiple_errors(self):
        """Test multiple validation errors are collected."""
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x, dependencies=["missing1"]))
        wf.add_node(Node("B", lambda x: x, dependencies=["missing2"]))

        result = wf.validate()

        assert result.valid is False
        assert len(result.errors) == 2

    def test_raise_if_invalid(self):
        """Test raise_if_invalid raises exception."""
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x, dependencies=["missing"]))

        result = wf.validate()

        with pytest.raises(ValidationError) as exc_info:
            result.raise_if_invalid()

        assert len(exc_info.value.errors) == 1

    def test_raise_if_invalid_does_nothing_when_valid(self):
        """Test raise_if_invalid does nothing for valid workflow."""
        wf = Workflow("test")
        wf.add_node(Node("A", lambda x: x))

        result = wf.validate()
        result.raise_if_invalid()  # Should not raise

    def test_validation_result_dataclass(self):
        """Test ValidationResult has expected fields."""
        result = ValidationResult(valid=True, errors=[], warnings=["warning"])

        assert result.valid is True
        assert result.errors == []
        assert result.warnings == ["warning"]
