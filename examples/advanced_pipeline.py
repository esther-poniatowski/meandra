"""
Advanced Pipeline Example
=========================

Demonstrates advanced features:
- Checkpointing
- Progress tracking
- Error handling
- Input/output contracts

Run with:
    python -m examples.advanced_pipeline
"""

import time
from typing import Any, Dict

from meandra.api import pipeline, node, build_workflow
from meandra.orchestration import SchedulingOrchestrator
from meandra.monitoring.progress import ProgressTracker
from meandra.checkpoint import CheckpointManager, FileSystemStorage


def validate_data_input(inputs: Dict[str, Any]) -> None:
    """Validate that input contains a non-empty data list."""
    assert "raw_data" in inputs, "Missing 'raw_data' input"
    assert isinstance(inputs["raw_data"], list), "'raw_data' must be a list"
    assert len(inputs["raw_data"]) > 0, "'raw_data' must not be empty"


def validate_numeric_output(outputs: Dict[str, Any]) -> None:
    """Validate that all output values are numeric."""
    for key, value in outputs.items():
        if isinstance(value, (int, float)):
            continue
        if isinstance(value, list):
            assert all(isinstance(x, (int, float)) for x in value), f"'{key}' contains non-numeric values"


@pipeline(name="advanced_analysis")
class AdvancedAnalysisPipeline:
    """An advanced pipeline with validation and checkpointing."""

    @node(
        outputs=["raw_data"],
        checkpointable=True
    )
    def load_data(self, inputs):
        """Simulate loading data from a source."""
        print("  [load_data] Loading data...")
        time.sleep(0.1)  # Simulate I/O
        return {"raw_data": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}

    @node(
        inputs=["raw_data"],
        outputs=["cleaned"],
        depends_on=["load_data"],
        checkpointable=True,
        input_contract=validate_data_input
    )
    def clean_data(self, inputs):
        """Clean the data by removing outliers."""
        print("  [clean_data] Cleaning data...")
        data = inputs["raw_data"]
        # Remove values outside 2 standard deviations
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std = variance ** 0.5
        cleaned = [x for x in data if abs(x - mean) <= 2 * std]
        return {"cleaned": cleaned}

    @node(
        inputs=["cleaned"],
        outputs=["normalized"],
        depends_on=["clean_data"],
        checkpointable=True,
        output_contract=validate_numeric_output
    )
    def normalize(self, inputs):
        """Normalize data to [0, 1] range."""
        print("  [normalize] Normalizing data...")
        data = inputs["cleaned"]
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val
        if range_val == 0:
            return {"normalized": [0.5] * len(data)}
        return {"normalized": [(x - min_val) / range_val for x in data]}

    @node(
        inputs=["normalized"],
        outputs=["features"],
        depends_on=["normalize"]
    )
    def extract_features(self, inputs):
        """Extract statistical features."""
        print("  [extract_features] Extracting features...")
        data = inputs["normalized"]
        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        return {
            "features": {
                "count": n,
                "mean": mean,
                "variance": variance,
                "std": variance ** 0.5,
                "min": min(data),
                "max": max(data),
            }
        }


def progress_callback(tracker: ProgressTracker) -> None:
    """Print progress updates."""
    print(f"  Progress: {tracker.percentage:.0f}% ({tracker.completed_count}/{tracker.total_nodes} nodes)")


def main():
    """Run the advanced pipeline."""
    print("=" * 60)
    print("Advanced Pipeline with Progress Tracking")
    print("=" * 60)

    # Build workflow with validation
    workflow = build_workflow(AdvancedAnalysisPipeline, validate=True)

    print(f"\nPipeline: {workflow.name}")
    print(f"Nodes: {list(workflow.nodes.keys())}")
    print(f"Checkpointable nodes: {[n.name for n in workflow.nodes.values() if n.is_checkpointable]}")

    # Set up progress tracking
    tracker = ProgressTracker(workflow.name, total_nodes=len(workflow.nodes))
    tracker.add_callback(progress_callback)

    # Run with orchestrator
    print("\nExecuting pipeline:")
    orchestrator = SchedulingOrchestrator()

    # Manually track progress (in production, orchestrator would do this)
    result = orchestrator.run(workflow, {})

    print("\nResults:")
    print(f"  Raw data: {result['raw_data'][:5]}... ({len(result['raw_data'])} items)")
    print(f"  Cleaned: {result['cleaned'][:5]}... ({len(result['cleaned'])} items)")
    print(f"  Normalized: [{result['normalized'][0]:.3f}, {result['normalized'][1]:.3f}, ...]")
    print(f"  Features: {result['features']}")

    # Demonstrate checkpoint capability
    print("\n" + "=" * 60)
    print("Checkpoint Manager Demo")
    print("=" * 60)

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = FileSystemStorage(tmpdir)
        manager = CheckpointManager(storage)

        # Save a checkpoint
        checkpoint_id = manager.save(
            workflow_name="advanced_analysis",
            node_name="normalize",
            node_index=2,
            data={"normalized": result["normalized"]},
            run_id="demo-run-001"
        )
        print(f"\nSaved checkpoint: {checkpoint_id}")

        # List checkpoints
        checkpoints = manager.list_checkpoints("advanced_analysis")
        print(f"Available checkpoints: {len(checkpoints)}")

        # Load latest
        latest = manager.load_latest("advanced_analysis")
        if latest:
            print(f"Latest checkpoint: node={latest.info.node_name}, run={latest.info.run_id}")


if __name__ == "__main__":
    main()
