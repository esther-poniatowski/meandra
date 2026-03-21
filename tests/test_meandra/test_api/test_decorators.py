"""
test_meandra.test_api.test_decorators
=====================================

Tests for meandra.api.decorators module.
"""

import pytest
from typing import Dict, Any

from meandra.api.decorators import (
    node,
    pipeline,
    NodeSpec,
    PipelineSpec,
    get_node_spec,
    get_pipeline_spec,
    is_node,
    is_pipeline,
    build_workflow,
)
from meandra.core.node import Node
from meandra.core.workflow import Workflow


class TestNodeDecorator:
    """Tests for @node decorator."""

    def test_node_without_arguments(self):
        """Test @node used without arguments."""
        @node
        def my_node(inputs):
            return {"out": 1}

        assert is_node(my_node)
        spec = get_node_spec(my_node)
        assert spec is not None
        assert spec.func.__name__ == "my_node"

    def test_node_with_arguments(self):
        """Test @node used with arguments."""
        @node(inputs=["a", "b"], outputs=["result"])
        def add(inputs):
            return {"result": inputs["a"] + inputs["b"]}

        assert is_node(add)
        spec = get_node_spec(add)
        assert spec is not None
        assert spec.inputs == ["a", "b"]
        assert spec.outputs == ["result"]

    def test_node_with_all_options(self):
        """Test @node with all options specified."""
        def input_check(inputs):
            assert "x" in inputs

        def output_check(outputs):
            assert "y" in outputs

        @node(
            name="custom_name",
            inputs=["x"],
            outputs=["y"],
            depends_on=["loader"],
            checkpointable=True,
            accepts_context=True,
            input_contract=input_check,
            output_contract=output_check,
        )
        def my_processor(inputs):
            return {"y": inputs["x"] * 2}

        spec = get_node_spec(my_processor)
        assert spec is not None
        assert spec.name == "custom_name"
        assert spec.inputs == ["x"]
        assert spec.outputs == ["y"]
        assert spec.dependencies == ["loader"]
        assert spec.is_checkpointable is True
        assert spec.accepts_context is True
        assert spec.input_contract is input_check
        assert spec.output_contract is output_check

    def test_node_preserves_function_behavior(self):
        """Test that decorated function still works normally."""
        @node(outputs=["result"])
        def compute(inputs):
            return {"result": inputs.get("value", 0) * 2}

        # Function should still be callable
        result = compute({"value": 5})
        assert result == {"result": 10}

    def test_node_spec_to_node(self):
        """Test converting NodeSpec to Node."""
        @node(inputs=["data"], outputs=["processed"], depends_on=["loader"])
        def process(inputs):
            return {"processed": inputs["data"]}

        spec = get_node_spec(process)
        node_obj = spec.to_node()

        assert isinstance(node_obj, Node)
        assert node_obj.name == "process"
        assert node_obj.inputs == ["data"]
        assert node_obj.outputs == ["processed"]
        assert node_obj.dependencies == ["loader"]

    def test_node_with_explicit_name(self):
        """Test @node with explicit name."""
        @node(name="renamed_node")
        def original_name(inputs):
            return {}

        spec = get_node_spec(original_name)
        assert spec.name == "renamed_node"

        node_obj = spec.to_node()
        assert node_obj.name == "renamed_node"

    def test_is_node_false_for_undecorated(self):
        """Test is_node returns False for undecorated functions."""
        def plain_function(inputs):
            return {}

        assert is_node(plain_function) is False
        assert get_node_spec(plain_function) is None


class TestPipelineDecorator:
    """Tests for @pipeline decorator."""

    def test_pipeline_without_arguments(self):
        """Test @pipeline used without arguments."""
        @pipeline
        class MyPipeline:
            @node(outputs=["data"])
            def load(self, inputs):
                return {"data": [1, 2, 3]}

        assert is_pipeline(MyPipeline)
        spec = get_pipeline_spec(MyPipeline)
        assert spec is not None
        assert spec.name == "MyPipeline"
        assert len(spec.node_specs) == 1

    def test_pipeline_with_name(self):
        """Test @pipeline with explicit name."""
        @pipeline(name="custom_pipeline")
        class SomePipeline:
            @node(outputs=["out"])
            def step1(self, inputs):
                return {"out": 1}

        spec = get_pipeline_spec(SomePipeline)
        assert spec.name == "custom_pipeline"

    def test_pipeline_discovers_nodes(self):
        """Test that @pipeline discovers @node decorated methods."""
        @pipeline(name="multi_step")
        class MultiStepPipeline:
            @node(outputs=["a"])
            def step_a(self, inputs):
                return {"a": 1}

            @node(inputs=["a"], outputs=["b"], depends_on=["step_a"])
            def step_b(self, inputs):
                return {"b": inputs["a"] * 2}

            @node(inputs=["b"], outputs=["c"], depends_on=["step_b"])
            def step_c(self, inputs):
                return {"c": inputs["b"] + 10}

            def helper_method(self):
                """Non-decorated helper should be ignored."""
                return "helper"

        spec = get_pipeline_spec(MultiStepPipeline)
        assert len(spec.node_specs) == 3

        node_names = {s.name for s in spec.node_specs}
        assert node_names == {"step_a", "step_b", "step_c"}

    def test_pipeline_preserves_definition_order(self):
        """Test that node specs preserve definition order."""
        @pipeline(name="ordered")
        class OrderedPipeline:
            @node(outputs=["a"])
            def step_a(self, inputs):
                return {"a": 1}

            @node(inputs=["a"], outputs=["b"], depends_on=["step_a"])
            def step_b(self, inputs):
                return {"b": 2}

        spec = get_pipeline_spec(OrderedPipeline)
        assert [s.name for s in spec.node_specs] == ["step_a", "step_b"]

    def test_pipeline_duplicate_names_raise(self):
        """Test duplicate node names raise an error."""
        with pytest.raises(ValueError, match="Duplicate node names"):
            @pipeline(name="dup")
            class DupPipeline:
                @node(name="dup")
                def step_a(self, inputs):
                    return {"a": 1}

                @node(name="dup")
                def step_b(self, inputs):
                    return {"b": 2}
            _ = DupPipeline

    def test_pipeline_ignores_private_methods(self):
        """Test that private methods are ignored."""
        @pipeline
        class PipelineWithPrivate:
            @node(outputs=["out"])
            def public_node(self, inputs):
                return {"out": 1}

            def _private_helper(self):
                return "private"

            def __dunder_method__(self):
                return "dunder"

        spec = get_pipeline_spec(PipelineWithPrivate)
        assert len(spec.node_specs) == 1
        assert spec.node_specs[0].name == "public_node"

    def test_is_pipeline_false_for_undecorated(self):
        """Test is_pipeline returns False for undecorated classes."""
        class PlainClass:
            pass

        assert is_pipeline(PlainClass) is False
        assert get_pipeline_spec(PlainClass) is None


class TestBuildWorkflow:
    """Tests for build_workflow function."""

    def test_build_workflow_basic(self):
        """Test building a workflow from a pipeline class."""
        @pipeline(name="test_workflow")
        class TestPipeline:
            @node(outputs=["data"])
            def load(self, inputs):
                return {"data": [1, 2, 3]}

            @node(inputs=["data"], outputs=["result"], depends_on=["load"])
            def process(self, inputs):
                return {"result": sum(inputs["data"])}

        workflow = build_workflow(TestPipeline)

        assert isinstance(workflow, Workflow)
        assert workflow.name == "test_workflow"
        assert len(workflow) == 2
        assert "load" in workflow
        assert "process" in workflow

    def test_build_workflow_with_instance(self):
        """Test building workflow with provided instance."""
        @pipeline(name="stateful")
        class StatefulPipeline:
            def __init__(self):
                self.multiplier = 10

            @node(inputs=["x"], outputs=["y"])
            def scale(self, inputs):
                return {"y": inputs["x"] * self.multiplier}

        instance = StatefulPipeline()
        instance.multiplier = 5

        workflow = build_workflow(StatefulPipeline, instance=instance)

        # Execute the node to verify instance binding
        scale_node = workflow.nodes["scale"]
        result = scale_node.execute({"x": 3})
        assert result == {"y": 15}  # 3 * 5

    def test_build_workflow_with_init_args(self):
        """Test building workflow with init args."""
        @pipeline(name="init_args")
        class InitPipeline:
            def __init__(self, factor: int):
                self.factor = factor

            @node(inputs=["x"], outputs=["y"])
            def scale(self, inputs):
                return {"y": inputs["x"] * self.factor}

        workflow = build_workflow(InitPipeline, init_args=(4,))
        result = workflow.nodes["scale"].execute({"x": 2})
        assert result == {"y": 8}

    def test_build_workflow_validate(self):
        """Test build_workflow validate option."""
        @pipeline(name="invalid_deps")
        class InvalidPipeline:
            @node(outputs=["a"], depends_on=["missing"])
            def step_a(self, inputs):
                return {"a": 1}

        with pytest.raises(Exception):  # ValidationError
            build_workflow(InvalidPipeline, validate=True)

    def test_build_workflow_error_for_non_pipeline(self):
        """Test that build_workflow raises error for non-pipeline class."""
        class NotAPipeline:
            pass

        with pytest.raises(ValueError, match="not decorated with @pipeline"):
            build_workflow(NotAPipeline)

    def test_build_workflow_preserves_dependencies(self):
        """Test that dependencies are preserved in built workflow."""
        @pipeline(name="deps_test")
        class DependencyPipeline:
            @node(outputs=["a"])
            def step_a(self, inputs):
                return {"a": 1}

            @node(outputs=["b"], depends_on=["step_a"])
            def step_b(self, inputs):
                return {"b": 2}

            @node(outputs=["c"], depends_on=["step_a", "step_b"])
            def step_c(self, inputs):
                return {"c": 3}

        workflow = build_workflow(DependencyPipeline)

        assert workflow.nodes["step_a"].dependencies == []
        assert workflow.nodes["step_b"].dependencies == ["step_a"]
        assert set(workflow.nodes["step_c"].dependencies) == {"step_a", "step_b"}


class TestDecoratorIntegration:
    """Integration tests for decorator API with orchestrator."""

    def test_complete_pipeline_execution(self):
        """Test complete pipeline definition and execution."""
        from meandra.orchestration.orchestrator import SchedulingOrchestrator

        @pipeline(name="integration_test")
        class DataPipeline:
            @node(outputs=["raw"])
            def load(self, inputs):
                return {"raw": [1, 2, 3, 4, 5]}

            @node(inputs=["raw"], outputs=["doubled"], depends_on=["load"])
            def double(self, inputs):
                return {"doubled": [x * 2 for x in inputs["raw"]]}

            @node(inputs=["doubled"], outputs=["total"], depends_on=["double"])
            def sum_all(self, inputs):
                return {"total": sum(inputs["doubled"])}

        workflow = build_workflow(DataPipeline)
        orchestrator = SchedulingOrchestrator()
        result = orchestrator.run(workflow, {})

        assert result["raw"] == [1, 2, 3, 4, 5]
        assert result["doubled"] == [2, 4, 6, 8, 10]
        assert result["total"] == 30

    def test_pipeline_with_initial_inputs(self):
        """Test pipeline execution with initial inputs."""
        from meandra.orchestration.orchestrator import SchedulingOrchestrator

        @pipeline(name="with_inputs")
        class InputPipeline:
            @node(inputs=["factor"], outputs=["scaled"])
            def scale(self, inputs):
                return {"scaled": inputs["factor"] * 10}

        workflow = build_workflow(InputPipeline)
        orchestrator = SchedulingOrchestrator()
        result = orchestrator.run(workflow, {"factor": 3})

        assert result["scaled"] == 30


class TestNodeSpecToNode:
    """Tests for NodeSpec.to_node method."""

    def test_to_node_without_instance(self):
        """Test to_node without instance for standalone functions."""
        @node(inputs=["x"], outputs=["y"], checkpointable=True)
        def standalone(inputs):
            return {"y": inputs["x"] + 1}

        spec = get_node_spec(standalone)
        node_obj = spec.to_node()

        assert node_obj.name == "standalone"
        assert node_obj.inputs == ["x"]
        assert node_obj.outputs == ["y"]
        assert node_obj.is_checkpointable is True

        # Execute should work
        result = node_obj.execute({"x": 5})
        assert result == {"y": 6}

    def test_to_node_with_instance(self):
        """Test to_node with instance for bound methods."""
        class Container:
            def __init__(self, factor):
                self.factor = factor

            @node(inputs=["x"], outputs=["y"])
            def multiply(self, inputs):
                return {"y": inputs["x"] * self.factor}

        container = Container(factor=3)
        spec = get_node_spec(Container.multiply)
        node_obj = spec.to_node(instance=container)

        result = node_obj.execute({"x": 4})
        assert result == {"y": 12}

    def test_to_node_name_fallback(self):
        """Test that node name falls back to function name."""
        @node
        def unnamed_node(inputs):
            return {}

        spec = get_node_spec(unnamed_node)
        node_obj = spec.to_node()
        assert node_obj.name == "unnamed_node"


if __name__ == "__main__":
    pytest.main()
