# Usage

Meandra defines and executes modular data processing pipelines. Pipelines are
built from decorated node functions, assembled into workflow classes, and run
through the CLI or the Python API.

For the full command registry, refer to [CLI Reference](cli-reference.md).

## Defining Computation Nodes

Each node declares its inputs, outputs, and dependencies:

```python
from meandra.api import node

@node(outputs=["data"])
def load_data(inputs):
    return {"data": [1, 2, 3, 4, 5]}

@node(inputs=["data"], outputs=["total"], depends_on=["load_data"])
def sum_data(inputs):
    return {"total": sum(inputs["data"])}
```

## Assembling a Pipeline

Nodes group into a pipeline class:

```python
from meandra.api import pipeline, node

@pipeline(name="my_pipeline")
class MyPipeline:
    @node(outputs=["data"])
    def load(self, inputs):
        return {"data": [1, 2, 3, 4, 5]}

    @node(inputs=["data"], outputs=["total"], depends_on=["load"])
    def process(self, inputs):
        return {"total": sum(inputs["data"])}
```

## Running a Pipeline from Python

```python
from meandra.api import build_workflow
from meandra.orchestration import SchedulingOrchestrator

workflow = build_workflow(MyPipeline, validate=True, available_inputs=set())
orchestrator = SchedulingOrchestrator()
result = orchestrator.run(workflow, {})
print(result["total"])  # 15
```

The `build_workflow` function validates the pipeline graph before execution,
catching missing dependencies and type mismatches early.

## Running a Pipeline from the CLI

The `run` command executes a pipeline from a Python module reference:

```sh
meandra run mymodule:MyPipeline --config config.yaml
```

Override parameters at runtime with `-p`:

```sh
meandra run mymodule:MyPipeline -p learning_rate=0.01 -p epochs=50
```

## Validating a Configuration

Check a configuration file against a pipeline's expected parameters before
running:

```sh
meandra validate config.yaml --pipeline mymodule:MyPipeline
```

## Visualizing the Workflow Graph

Export the dependency graph as an image for inspection:

```sh
meandra graph mymodule:MyPipeline --output workflow.png
```

## Using the Fluent API

An alternative to class-based pipelines for simple workflows:

```python
from meandra.api import step, pipe

workflow = (
    pipe("data_pipeline")
    .add(step(load_data).out("data"))
    .add(step(process).in_("data").out("result").depends_on("load_data"))
    .build()
)
```

## Next Steps

- [Concepts](concepts.md) — Core abstractions and design.
- [Tutorials](tutorials.md) — Step-by-step walkthroughs.
- [API Reference](../api/index.md) — Python API documentation.
