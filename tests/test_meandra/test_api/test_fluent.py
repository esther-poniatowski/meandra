"""
test_meandra.test_api.test_fluent
=================================

Tests for meandra.api.fluent module.
"""

import pytest
from typing import Dict, Any

from meandra.api.fluent import (
    StepBuilder,
    PipelineBuilder,
    step,
    pipe,
)
from meandra.core.node import Node
from meandra.core.workflow import Workflow


class TestStepBuilder:
    """Tests for StepBuilder."""

    def test_step_creates_builder(self):
        """Test step() creates a StepBuilder."""
        def my_func(inputs):
            return {"out": 1}

        builder = step(my_func)
        assert isinstance(builder, StepBuilder)
        assert builder.func is my_func

    def test_builder_fluent_chain(self):
        """Test fluent method chaining."""
        def my_func(inputs):
            return {"result": inputs["a"] + inputs["b"]}

        builder = (
            step(my_func)
            .in_("a", "b")
            .out("result")
            .depends_on("loader")
            .checkpointable()
            .context()
        )

        assert builder.inputs == ["a", "b"]
        assert builder.outputs == ["result"]
        assert builder.dependencies == ["loader"]
        assert builder.is_checkpointable is True
        assert builder.accepts_context is True

    def test_builder_named(self):
        """Test setting explicit name."""
        def my_func(inputs):
            return {}

        builder = step(my_func).named("custom_name")
        assert builder.name == "custom_name"

        node = builder.build()
        assert node.name == "custom_name"

    def test_builder_build_creates_node(self):
        """Test build() creates a Node."""
        def process(inputs):
            return {"out": inputs["x"] * 2}

        node = (
            step(process)
            .in_("x")
            .out("out")
            .depends_on("source")
            .build()
        )

        assert isinstance(node, Node)
        assert node.name == "process"
        assert node.inputs == ["x"]
        assert node.outputs == ["out"]
        assert node.dependencies == ["source"]

    def test_builder_uses_function_name_if_not_set(self):
        """Test builder uses function name by default."""
        def my_function(inputs):
            return {}

        node = step(my_function).build()
        assert node.name == "my_function"

    def test_builder_checkpointable_toggle(self):
        """Test checkpointable with explicit True/False."""
        def my_func(inputs):
            return {}

        builder = step(my_func).checkpointable(True)
        assert builder.is_checkpointable is True

        builder = builder.checkpointable(False)
        assert builder.is_checkpointable is False

    def test_builder_context_toggle(self):
        """Test context with explicit True/False."""
        def my_func(inputs):
            return {}

        builder = step(my_func).context(True)
        assert builder.accepts_context is True

        builder = builder.context(False)
        assert builder.accepts_context is False

    def test_builder_with_input_contract(self):
        """Test setting input contract."""
        def my_func(inputs):
            return {}

        def validate_input(inputs):
            assert "required" in inputs

        builder = step(my_func).with_input_contract(validate_input)
        assert builder.input_contract is validate_input

        node = builder.build()
        assert node.input_contract is validate_input

    def test_builder_with_output_contract(self):
        """Test setting output contract."""
        def my_func(inputs):
            return {}

        def validate_output(outputs):
            assert "result" in outputs

        builder = step(my_func).with_output_contract(validate_output)
        assert builder.output_contract is validate_output

        node = builder.build()
        assert node.output_contract is validate_output


class TestPipelineBuilder:
    """Tests for PipelineBuilder."""

    def test_pipe_creates_builder(self):
        """Test pipe() creates a PipelineBuilder."""
        builder = pipe("my_workflow")
        assert isinstance(builder, PipelineBuilder)
        assert builder.name == "my_workflow"

    def test_pipeline_add_steps(self):
        """Test adding steps to pipeline."""
        def load(inputs):
            return {"data": [1, 2, 3]}

        def process(inputs):
            return {"result": sum(inputs["data"])}

        builder = (
            pipe("example")
            .add(step(load).out("data"))
            .add(step(process).in_("data").out("result").depends_on("load"))
        )

        assert len(builder.steps) == 2

    def test_pipeline_build_creates_workflow(self):
        """Test build() creates a Workflow."""
        def load(inputs):
            return {"data": [1, 2, 3]}

        def process(inputs):
            return {"result": sum(inputs["data"])}

        workflow = (
            pipe("example")
            .add(step(load).out("data"))
            .add(step(process).in_("data").out("result").depends_on("load"))
            .build()
        )

        assert isinstance(workflow, Workflow)
        assert workflow.name == "example"
        assert len(workflow) == 2
        assert "load" in workflow
        assert "process" in workflow

    def test_pipeline_duplicate_names_raise(self):
        """Test duplicate node names raise error."""
        def load(inputs):
            return {"data": [1, 2, 3]}

        builder = pipe("dup")
        builder.add(step(load).out("data"))
        builder.add(step(load).out("data2"))

        with pytest.raises(ValueError, match="Duplicate node name"):
            builder.build()

    def test_pipeline_empty_build(self):
        """Test building empty pipeline."""
        workflow = pipe("empty").build()
        assert len(workflow) == 0
        assert workflow.name == "empty"

    def test_pipeline_method_chaining(self):
        """Test that add() returns self for chaining."""
        def f1(inputs):
            return {}

        def f2(inputs):
            return {}

        builder = pipe("chain")
        result = builder.add(step(f1))
        assert result is builder

        result = builder.add(step(f2))
        assert result is builder


class TestFluentAPIIntegration:
    """Integration tests for fluent API."""

    def test_complete_workflow_with_fluent_api(self):
        """Test complete workflow definition and execution."""
        from meandra.orchestration.orchestrator import SchedulingOrchestrator

        def load_data(inputs):
            return {"raw": [1, 2, 3, 4, 5]}

        def transform(inputs):
            return {"transformed": [x * 2 for x in inputs["raw"]]}

        def aggregate(inputs):
            return {"total": sum(inputs["transformed"])}

        workflow = (
            pipe("data_pipeline")
            .add(step(load_data).out("raw"))
            .add(step(transform).in_("raw").out("transformed").depends_on("load_data"))
            .add(step(aggregate).in_("transformed").out("total").depends_on("transform"))
            .build()
        )

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(workflow, {})

        assert results["raw"] == [1, 2, 3, 4, 5]
        assert results["transformed"] == [2, 4, 6, 8, 10]
        assert results["total"] == 30

    def test_workflow_with_initial_inputs(self):
        """Test workflow with initial inputs."""
        from meandra.orchestration.orchestrator import SchedulingOrchestrator

        def scale(inputs):
            return {"scaled": inputs["factor"] * inputs["value"]}

        workflow = (
            pipe("scale_pipeline")
            .add(step(scale).in_("factor", "value").out("scaled"))
            .build()
        )

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(workflow, {"factor": 3, "value": 10})

        assert results["scaled"] == 30

    def test_checkpointable_node_in_workflow(self):
        """Test checkpointable node flags are preserved."""
        def checkpoint_me(inputs):
            return {"out": 1}

        workflow = (
            pipe("checkpoint_test")
            .add(step(checkpoint_me).out("out").checkpointable(True))
            .build()
        )

        node = workflow.nodes["checkpoint_me"]
        assert node.is_checkpointable is True


if __name__ == "__main__":
    pytest.main()
