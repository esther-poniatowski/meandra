"""
Simple Pipeline Example
=======================

Demonstrates basic pipeline definition using the decorator API.

Run with:
    python -m examples.simple_pipeline

Or via CLI:
    meandra run examples.simple_pipeline:DataProcessingPipeline
"""

from meandra.api import pipeline, node, build_workflow
from meandra.orchestration import SchedulingOrchestrator


@pipeline(name="data_processing")
class DataProcessingPipeline:
    """A simple data processing pipeline."""

    @node(outputs=["raw_data"])
    def load_data(self, inputs):
        """Load raw data."""
        print("Loading data...")
        return {"raw_data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

    @node(inputs=["raw_data"], outputs=["filtered"], depends_on=["load_data"])
    def filter_data(self, inputs):
        """Filter data to keep only even numbers."""
        print("Filtering data...")
        data = inputs["raw_data"]
        return {"filtered": [x for x in data if x % 2 == 0]}

    @node(inputs=["filtered"], outputs=["doubled"], depends_on=["filter_data"])
    def transform_data(self, inputs):
        """Double each value."""
        print("Transforming data...")
        return {"doubled": [x * 2 for x in inputs["filtered"]]}

    @node(inputs=["doubled"], outputs=["total"], depends_on=["transform_data"])
    def aggregate(self, inputs):
        """Sum all values."""
        print("Aggregating data...")
        return {"total": sum(inputs["doubled"])}


def main():
    """Run the pipeline."""
    # Build the workflow from the decorated class
    workflow = build_workflow(DataProcessingPipeline)

    print(f"Pipeline: {workflow.name}")
    print(f"Nodes: {list(workflow.nodes.keys())}")
    print()

    # Create orchestrator and run
    orchestrator = SchedulingOrchestrator()
    result = orchestrator.run(workflow, {})

    print()
    print("Results:")
    print(f"  Raw data: {result['raw_data']}")
    print(f"  Filtered (even): {result['filtered']}")
    print(f"  Doubled: {result['doubled']}")
    print(f"  Total: {result['total']}")


if __name__ == "__main__":
    main()
