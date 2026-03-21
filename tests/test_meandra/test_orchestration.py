"""
Tests for workflow orchestration.
"""

import pytest

from meandra import (
    Node,
    Workflow,
    SchedulingOrchestrator,
    WorkflowExecutionError,
    InMemoryStateTracker,
    NodeState,
    HookEvent,
)


class TestSchedulingOrchestrator:
    """Tests for SchedulingOrchestrator."""

    def test_simple_workflow_execution(self):
        """Test executing a simple workflow."""

        def load_data(inputs):
            return {"data": [1, 2, 3]}

        def process(inputs):
            return {"result": sum(inputs["data"])}

        wf = Workflow("simple")
        wf.add_node(Node("loader", load_data, outputs=["data"]))
        wf.add_node(
            Node("processor", process, dependencies=["loader"], inputs=["data"], outputs=["result"])
        )

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(wf, {})

        assert results["data"] == [1, 2, 3]
        assert results["result"] == 6

    def test_workflow_with_initial_inputs(self):
        """Test workflow receives initial inputs."""

        def multiply(inputs):
            return {"product": inputs["x"] * inputs["y"]}

        wf = Workflow("multiply")
        wf.add_node(Node("multiplier", multiply, inputs=["x", "y"], outputs=["product"]))

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(wf, {"x": 3, "y": 4})

        assert results["product"] == 12

    def test_workflow_data_flows_between_nodes(self):
        """Test data flows correctly between dependent nodes."""

        def generate(inputs):
            return {"values": list(range(inputs["n"]))}

        def square(inputs):
            return {"squared": [x**2 for x in inputs["values"]]}

        def total(inputs):
            return {"sum": sum(inputs["squared"])}

        wf = Workflow("pipeline")
        wf.add_node(Node("generate", generate, inputs=["n"], outputs=["values"]))
        wf.add_node(
            Node("square", square, dependencies=["generate"], inputs=["values"], outputs=["squared"])
        )
        wf.add_node(
            Node("total", total, dependencies=["square"], inputs=["squared"], outputs=["sum"])
        )

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(wf, {"n": 5})

        assert results["values"] == [0, 1, 2, 3, 4]
        assert results["squared"] == [0, 1, 4, 9, 16]
        assert results["sum"] == 30

    def test_fail_fast_mode(self):
        """Test fail_fast stops execution on error."""

        def fail_node(inputs):
            raise ValueError("Intentional failure")

        def after_fail(inputs):
            return {"result": "should not run"}

        wf = Workflow("fail_fast_test")
        wf.add_node(Node("failing", fail_node, outputs=["output"]))
        wf.add_node(Node("after", after_fail, dependencies=["failing"]))

        orchestrator = SchedulingOrchestrator(fail_fast=True)

        with pytest.raises(WorkflowExecutionError) as exc_info:
            orchestrator.run(wf, {})

        assert exc_info.value.node_name == "failing"
        assert "Intentional failure" in str(exc_info.value)

    def test_continue_on_failure_mode(self):
        """Test continue mode skips dependents of failed nodes."""

        def success_node(inputs):
            return {"success_output": "ok"}

        def fail_node(inputs):
            raise ValueError("Intentional failure")

        def dependent_node(inputs):
            return {"dependent_output": "should not run"}

        wf = Workflow("continue_test")
        wf.add_node(Node("success", success_node, outputs=["success_output"]))
        wf.add_node(Node("failing", fail_node, outputs=["fail_output"]))
        wf.add_node(Node("dependent", dependent_node, dependencies=["failing"]))

        orchestrator = SchedulingOrchestrator(fail_fast=False)
        results = orchestrator.run(wf, {})

        assert results["success_output"] == "ok"
        assert "dependent_output" not in results

    def test_state_tracking(self):
        """Test state tracker is updated correctly."""

        def node_func(inputs):
            return {"output": "done"}

        wf = Workflow("tracked")
        wf.add_node(Node("node1", node_func, outputs=["output"]))

        tracker = InMemoryStateTracker("tracked", "test_run")
        orchestrator = SchedulingOrchestrator(state_tracker=tracker)
        orchestrator.run(wf, {})

        assert tracker.get_state("node1") == NodeState.COMPLETED
        assert tracker.get_outputs("node1") == {"output": "done"}

    def test_parallel_nodes_execute(self):
        """Test nodes in parallel layer all execute."""
        results_collector = []

        def make_collector(name):
            def collector(inputs):
                results_collector.append(name)
                return {f"{name}_output": name}
            return collector

        wf = Workflow("parallel")
        wf.add_node(Node("a", make_collector("a"), outputs=["a_output"]))
        wf.add_node(Node("b", make_collector("b"), outputs=["b_output"]))
        wf.add_node(Node("c", make_collector("c"), outputs=["c_output"]))

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(wf, {})

        assert set(results_collector) == {"a", "b", "c"}
        assert results["a_output"] == "a"
        assert results["b_output"] == "b"
        assert results["c_output"] == "c"

    def test_hooks_are_called(self):
        """Test lifecycle hooks are called."""
        events = []

        def before_workflow(workflow, inputs):
            events.append(("before_workflow", workflow.name))

        def after_workflow(workflow, inputs, outputs):
            events.append(("after_workflow", workflow.name))

        def before_node(node, inputs):
            events.append(("before_node", node.name))

        def after_node(node, inputs, outputs):
            events.append(("after_node", node.name))

        def on_error(node, error, context):
            events.append(("on_error", node.name))

        wf = Workflow("hooked")
        wf.add_node(Node("n1", lambda x: {"out": 1}, outputs=["out"]))

        orchestrator = SchedulingOrchestrator()
        orchestrator.add_hook(HookEvent.BEFORE_WORKFLOW, before_workflow)
        orchestrator.add_hook(HookEvent.AFTER_WORKFLOW, after_workflow)
        orchestrator.add_hook(HookEvent.BEFORE_NODE, before_node)
        orchestrator.add_hook(HookEvent.AFTER_NODE, after_node)
        orchestrator.add_hook(HookEvent.ON_ERROR, on_error)

        orchestrator.run(wf, {})

        assert ("before_workflow", "hooked") in events
        assert ("after_workflow", "hooked") in events
        assert ("before_node", "n1") in events
        assert ("after_node", "n1") in events
        assert ("on_error", "n1") not in events

    def test_hook_invalid_signature_raises(self):
        """Test hook signature validation."""
        wf = Workflow("hooked")
        wf.add_node(Node("n1", lambda x: {"out": 1}, outputs=["out"]))

        orchestrator = SchedulingOrchestrator()

        def invalid_hook():
            pass

        with pytest.raises(ValueError, match="must accept"):
            orchestrator.add_hook(HookEvent.BEFORE_NODE, invalid_hook)

    def test_parallel_fail_fast_raises(self):
        """Test fail_fast in parallel execution."""
        def ok(inputs):
            return {"ok_a": True}

        def fail(inputs):
            raise ValueError("boom")

        wf = Workflow("parallel_fail")
        wf.add_node(Node("a", ok, outputs=["ok_a"]))
        wf.add_node(Node("b", fail, outputs=["fail_b"]))

        orchestrator = SchedulingOrchestrator(max_workers=2, fail_fast=True)

        with pytest.raises(WorkflowExecutionError):
            orchestrator.run(wf, {})

    def test_parallel_continue_collects_success(self):
        """Test parallel execution continues when fail_fast is False."""
        def ok(inputs):
            return {"ok_a": True}

        def fail(inputs):
            raise ValueError("boom")

        wf = Workflow("parallel_continue")
        wf.add_node(Node("a", ok, outputs=["ok_a"]))
        wf.add_node(Node("b", fail, outputs=["fail_b"]))

        orchestrator = SchedulingOrchestrator(max_workers=2, fail_fast=False)
        results = orchestrator.run(wf, {})

        assert results["ok_a"] is True

    def test_diamond_workflow(self):
        """Test diamond-shaped workflow executes correctly."""

        def start(inputs):
            return {"value": 10}

        def double(inputs):
            return {"doubled": inputs["value"] * 2}

        def triple(inputs):
            return {"tripled": inputs["value"] * 3}

        def combine(inputs):
            return {"result": inputs["doubled"] + inputs["tripled"]}

        wf = Workflow("diamond")
        wf.add_node(Node("start", start, outputs=["value"]))
        wf.add_node(Node("double", double, dependencies=["start"], inputs=["value"], outputs=["doubled"]))
        wf.add_node(Node("triple", triple, dependencies=["start"], inputs=["value"], outputs=["tripled"]))
        wf.add_node(
            Node("combine", combine, dependencies=["double", "triple"], inputs=["doubled", "tripled"], outputs=["result"])
        )

        orchestrator = SchedulingOrchestrator()
        results = orchestrator.run(wf, {})

        assert results["value"] == 10
        assert results["doubled"] == 20
        assert results["tripled"] == 30
        assert results["result"] == 50
