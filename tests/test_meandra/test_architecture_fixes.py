from __future__ import annotations

import pytest

from meandra import CheckpointError, CheckpointManager, FileSystemStorage, Node, Workflow
from meandra.api import pipe, step
from meandra.integration.tessara import TessaraNodeAdapter


def test_fluent_pipeline_compiles_to_canonical_pipeline_spec() -> None:
    def load(inputs):
        return {"data": [1, 2, 3]}

    def process(inputs):
        return {"result": sum(inputs["data"])}

    builder = (
        pipe("canonical")
        .add(step(load).out("data"))
        .add(step(process).in_("data").out("result").depends_on("load"))
    )

    spec = builder.to_spec()
    workflow = spec.build()

    assert spec.name == "canonical"
    assert [node.name for node in workflow.nodes.values()] == ["load", "process"]
    assert spec.required_inputs() == set()


def test_tessara_adapter_transforms_nodes_without_rebuilding_field_by_field() -> None:
    workflow = Workflow("adapter")
    workflow.add_node(Node("node1", lambda inputs: {"out": inputs["x"]}, inputs=["x"], outputs=["out"]))

    adapter = TessaraNodeAdapter(params=type("Params", (), {"to_dict": lambda self, values_only=True: {}, "data": {}})())  # type: ignore[arg-type]
    adapted = adapter.adapt_workflow(workflow, node_params={})

    assert adapted.nodes["node1"].name == "node1"
    assert adapted.nodes["node1"].outputs == ["out"]
    assert adapted.nodes["node1"] is workflow.nodes["node1"]


def test_checkpoint_resume_plan_fails_closed_on_workflow_hash_mismatch(tmp_path) -> None:
    storage = FileSystemStorage(tmp_path)
    manager = CheckpointManager(storage)

    original = Workflow("resume")
    original.add_node(Node("start", lambda inputs: {"x": 1}, outputs=["x"], is_checkpointable=True))
    checkpoint_id = manager.save(
        workflow_name=original.name,
        node_name="start",
        node_index=0,
        data={"x": 1},
        run_id="run-1",
        context={"x": 1},
        workflow_hash=original.structure_hash(),
        workflow_state={"inputs": {}, "artifacts": {"x": 1}},
        completed_nodes=["start"],
    )
    checkpoint = manager.load(checkpoint_id)
    assert checkpoint is not None

    changed = Workflow("resume")
    changed.add_node(Node("other", lambda inputs: {"y": 2}, outputs=["y"], is_checkpointable=True))

    with pytest.raises(CheckpointError, match="incompatible"):
        manager.build_resume_plan(changed, checkpoint)
