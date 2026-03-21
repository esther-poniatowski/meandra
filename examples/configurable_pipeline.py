"""
Configurable Pipeline Example
=============================

Demonstrates a pipeline that accepts configuration parameters.

Run with:
    python -m examples.configurable_pipeline

Or via CLI with config:
    meandra run examples.configurable_pipeline:ScalingPipeline --config examples/config.json
"""

import json
from pathlib import Path

from meandra.api import pipeline, node, build_workflow
from meandra.orchestration import SchedulingOrchestrator


@pipeline(name="scaling_pipeline")
class ScalingPipeline:
    """A pipeline that scales data based on configuration."""

    def __init__(self, scale_factor: float = 1.0, offset: float = 0.0):
        self.scale_factor = scale_factor
        self.offset = offset

    @node(inputs=["data"], outputs=["scaled"])
    def scale(self, inputs):
        """Scale input data by configured factor."""
        data = inputs["data"]
        return {"scaled": [x * self.scale_factor for x in data]}

    @node(inputs=["scaled"], outputs=["shifted"], depends_on=["scale"])
    def shift(self, inputs):
        """Shift scaled data by configured offset."""
        scaled = inputs["scaled"]
        return {"shifted": [x + self.offset for x in scaled]}

    @node(inputs=["shifted"], outputs=["stats"], depends_on=["shift"])
    def compute_stats(self, inputs):
        """Compute statistics on transformed data."""
        data = inputs["shifted"]
        return {
            "stats": {
                "min": min(data),
                "max": max(data),
                "mean": sum(data) / len(data),
                "count": len(data),
            }
        }


def main():
    """Run the pipeline with different configurations."""
    # Configuration 1: Default
    print("=" * 50)
    print("Configuration 1: Default (scale=1.0, offset=0.0)")
    print("=" * 50)

    workflow = build_workflow(ScalingPipeline)
    orchestrator = SchedulingOrchestrator()
    result = orchestrator.run(workflow, {"data": [1, 2, 3, 4, 5]})

    print(f"Input: [1, 2, 3, 4, 5]")
    print(f"Scaled: {result['scaled']}")
    print(f"Shifted: {result['shifted']}")
    print(f"Stats: {result['stats']}")

    # Configuration 2: Custom scale and offset
    print()
    print("=" * 50)
    print("Configuration 2: Custom (scale=2.0, offset=10.0)")
    print("=" * 50)

    workflow = build_workflow(ScalingPipeline, init_args=(2.0, 10.0))
    result = orchestrator.run(workflow, {"data": [1, 2, 3, 4, 5]})

    print(f"Input: [1, 2, 3, 4, 5]")
    print(f"Scaled: {result['scaled']}")
    print(f"Shifted: {result['shifted']}")
    print(f"Stats: {result['stats']}")

    # Configuration 3: Using init_kwargs
    print()
    print("=" * 50)
    print("Configuration 3: Using kwargs (scale=0.5, offset=-5.0)")
    print("=" * 50)

    workflow = build_workflow(
        ScalingPipeline,
        init_kwargs={"scale_factor": 0.5, "offset": -5.0}
    )
    result = orchestrator.run(workflow, {"data": [10, 20, 30, 40, 50]})

    print(f"Input: [10, 20, 30, 40, 50]")
    print(f"Scaled: {result['scaled']}")
    print(f"Shifted: {result['shifted']}")
    print(f"Stats: {result['stats']}")


if __name__ == "__main__":
    main()
