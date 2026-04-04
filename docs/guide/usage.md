# Usage

Meandra defines and executes modular data processing pipelines. Pipelines are
built from decorated node functions, assembled into workflow classes, and run
through the CLI or the Python API.

For full command details, see the [CLI Reference](cli-reference.md).
For configuration file format, see [Configuration](configuration.md).

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

### Node Contracts

Nodes can enforce type constraints on inputs and outputs:

```python
import numpy as np
from meandra.integration.data import create_typed_node

node = create_typed_node(
    "processor",
    process_fn,
    input_types={"data": np.ndarray},
    output_types={"result": np.ndarray},
)
```

Contract validation runs before and after node execution, raising `TypeError`
on mismatches.

### Checkpointable Nodes

Mark nodes whose outputs should be persisted for workflow resumption:

```python
@node(outputs=["model"], depends_on=["prepare"], checkpointable=True)
def train(inputs):
    return {"model": fit_model(inputs["features"])}
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

`build_workflow` validates the pipeline graph before execution, catching
missing dependencies and type mismatches early.

## Running a Pipeline from the CLI

The `run` command executes a pipeline from a Python module reference:

```sh
meandra run mymodule:MyPipeline --config config.yaml
```

Override parameters at runtime with `--param` / `-p`:

```sh
meandra run mymodule:MyPipeline -p learning_rate=0.01 -p epochs=50
```

Save results to a JSON file with `--output` / `-o`:

```sh
meandra run mymodule:MyPipeline --config config.yaml -o results.json
```

Enable diagnostic output with `--verbose` / `-v`:

```sh
meandra run mymodule:MyPipeline -v --config config.yaml
```

## Validating a Configuration

Check a configuration file against a pipeline's expected parameters before
running:

```sh
meandra validate config.yaml --pipeline mymodule:MyPipeline
```

## Visualizing the Workflow Graph

Export the dependency graph for inspection. Supported output formats: DOT, PNG,
SVG, PDF.

```sh
meandra graph mymodule:MyPipeline --output workflow.png
meandra graph mymodule:MyPipeline --output workflow.dot
```

Without `--output`, the DOT representation prints to stdout.

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

## Checkpoint and Resumption

`CheckpointManager` saves node outputs to disk after each checkpointable node.
On failure, the next run resumes from the latest checkpoint:

```python
from meandra import CheckpointManager, SchedulingOrchestrator

manager = CheckpointManager.with_filesystem("/tmp/checkpoints", retention=5)
orchestrator = SchedulingOrchestrator(checkpoint_manager=manager)
result = orchestrator.run(workflow, inputs)
```

`FileSystemStorage` compresses checkpoint data with gzip. The `retention`
parameter limits the number of checkpoints kept per workflow.

## Data Catalog

`DataCatalog` maps logical dataset names to file paths with templated
placeholders:

```python
from meandra import DataCatalog

catalog = DataCatalog("/data")
catalog.register("raw", "{run_id}/raw.npy")
catalog.register("processed", "{run_id}/processed.pkl")

catalog.save("raw", data, run_id="run_001")
loaded = catalog.load("raw", run_id="run_001")
```

Built-in IO handlers cover Pickle (`.pkl`), NumPy (`.npy`, `.npz`), JSON
(`.json`), and YAML (`.yaml`). Custom handlers can be registered through
`HandlerRegistry`.

## Retry

Wrap unreliable operations with exponential backoff:

```python
from meandra.monitoring.retry import RetryConfig, retry

@retry(max_attempts=3, base_delay=1.0, retryable_exceptions=(IOError,))
def flaky_load(inputs):
    return {"data": fetch_remote(inputs["url"])}
```

`RetryConfig` can also be passed to `SchedulingOrchestrator` to apply retries
across all nodes:

```python
config = RetryConfig(max_attempts=3, base_delay=0.5, jitter=True)
orchestrator = SchedulingOrchestrator(retry_config=config)
```

## Progress Tracking

`ProgressTracker` reports node completion counts, timing, and percentage:

```python
from meandra.monitoring.progress import ProgressTracker

tracker = ProgressTracker("my_workflow", total_nodes=5)
tracker.add_callback(lambda t: print(t.summary()))
orchestrator = SchedulingOrchestrator(progress_tracker=tracker)
```

## State Tracking

`InMemoryStateTracker` records node states (pending, running, completed,
failed, skipped) during execution. `FileStateTracker` persists state changes as
JSON lines for post-mortem analysis:

```python
from meandra import FileStateTracker

tracker = FileStateTracker("my_workflow", "run_001", "state.jsonl")
orchestrator = SchedulingOrchestrator(state_tracker=tracker)
```

## Lifecycle Hooks

Register callbacks for workflow and node events:

```python
from meandra import SchedulingOrchestrator, HookEvent

orchestrator = SchedulingOrchestrator()
orchestrator.add_hook(HookEvent.BEFORE_NODE, lambda node, inputs: print(f"Starting {node.name}"))
orchestrator.add_hook(HookEvent.AFTER_NODE, lambda node, inputs, outputs: print(f"Done {node.name}"))
orchestrator.add_hook(HookEvent.ON_ERROR, lambda node, exc, ctx: print(f"Failed {node.name}: {exc}"))
```

Available events: `BEFORE_WORKFLOW`, `AFTER_WORKFLOW`, `BEFORE_NODE`,
`AFTER_NODE`, `ON_ERROR`.

## Parallel Execution

Independent nodes within the same DAG layer run concurrently when
`max_workers` is set:

```python
orchestrator = SchedulingOrchestrator(max_workers=4)
```

## Logging Configuration

Configure structured logging with workflow context injection:

```python
from meandra.logging.config import configure_logging, LogLevel

configure_logging(level=LogLevel.DEBUG, log_file="workflow.log")
```

Log messages automatically include `run_id`, `workflow_name`, and `node_name`
when execution context is active.

## Tessara Integration

`TessaraNodeAdapter` injects Tessara parameters into node functions.
`SweepOrchestrator` runs a workflow across all parameter combinations from a
`ParamSweeper`:

```python
from tessara import ParameterSet, Param, ParamSweeper
from meandra.integration.tessara import TessaraNodeAdapter, SweepOrchestrator

params = ParameterSet(lr=Param(default=0.01))
adapter = TessaraNodeAdapter(params)
adapted_workflow = adapter.adapt_workflow(workflow)

sweeper = ParamSweeper(params)
sweep = SweepOrchestrator(orchestrator, sweeper)
results = sweep.run_sweep(workflow, inputs)
```

## Morpha Integration

`DataStructureIOHandler` bridges Meandra's IO system with Morpha's
`Saver`/`Loader` classes, supporting auto-detection by file extension:

```python
from meandra.integration.data import DataStructureIOHandler

handler = DataStructureIOHandler()
handler.write("output.h5", data_structure)
loaded = handler.read("output.h5")
```

## WorkflowModel

`Workflow.build_model()` returns a canonical `WorkflowModel` summarizing nodes,
edges, inputs, and outputs for inspection or serialization:

```python
model = workflow.build_model()
print(model.inputs)   # ["data_path"]
print(model.outputs)  # ["result", "metrics"]
print(model.edges)    # [("load", "process"), ...]
```

## Next Steps

- [CLI Reference](cli-reference.md) -- Full command and option listing.
- [Configuration](configuration.md) -- Configuration file format.
- [Concepts](concepts.md) -- Core abstractions and design.
- [Tutorials](tutorials.md) -- Step-by-step walkthroughs.
- [API Reference](../api/index.md) -- Python API documentation.
