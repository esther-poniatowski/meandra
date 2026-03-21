"""
Fluent API Example
==================

Demonstrates pipeline definition using the fluent (builder) API.

Run with:
    python -m examples.fluent_api_example
"""

from meandra.api import step, pipe
from meandra.orchestration import SchedulingOrchestrator


def load_numbers(inputs):
    """Load a sequence of numbers."""
    return {"numbers": list(range(1, 11))}


def compute_squares(inputs):
    """Compute squares of input numbers."""
    return {"squares": [x**2 for x in inputs["numbers"]]}


def compute_sum(inputs):
    """Sum all squared values."""
    return {"sum_of_squares": sum(inputs["squares"])}


def compute_mean(inputs):
    """Compute mean of squared values."""
    squares = inputs["squares"]
    return {"mean_of_squares": sum(squares) / len(squares)}


def main():
    """Run the pipeline."""
    # Build workflow using fluent API
    workflow = (
        pipe("statistics_pipeline")
        .add(step(load_numbers).out("numbers"))
        .add(step(compute_squares).in_("numbers").out("squares").depends_on("load_numbers"))
        .add(step(compute_sum).in_("squares").out("sum_of_squares").depends_on("compute_squares"))
        .add(step(compute_mean).in_("squares").out("mean_of_squares").depends_on("compute_squares"))
        .build()
    )

    print(f"Pipeline: {workflow.name}")
    print(f"Nodes: {list(workflow.nodes.keys())}")
    print()

    # Run the workflow
    orchestrator = SchedulingOrchestrator()
    result = orchestrator.run(workflow, {})

    print("Results:")
    print(f"  Numbers: {result['numbers']}")
    print(f"  Squares: {result['squares']}")
    print(f"  Sum of squares: {result['sum_of_squares']}")
    print(f"  Mean of squares: {result['mean_of_squares']}")


if __name__ == "__main__":
    main()
