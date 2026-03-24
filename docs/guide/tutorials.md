# Tutorials

These tutorials walk through common use cases for Meandra.

## Tutorial 1: Building a Data Processing Pipeline

This tutorial builds a complete data processing pipeline.

**Step 1: Define data transformations**

```python
import numpy as np

def load_data(path):
    return np.load(path)

def normalize(data):
    return (data - data.mean()) / data.std()

def compute_features(data):
    return {"mean": data.mean(), "std": data.std()}
```

**Step 2: Create a pipeline class**

```python
from meandra.api import pipeline, node, build_workflow

@pipeline(name="feature_extraction")
class FeaturePipeline:
    def __init__(self, data_path: str):
        self.data_path = data_path

    @node(outputs=["raw"])
    def load(self, inputs):
        return {"raw": load_data(self.data_path)}

    @node(inputs=["raw"], outputs=["normalized"], depends_on=["load"])
    def normalize(self, inputs):
        return {"normalized": normalize(inputs["raw"])}

    @node(inputs=["normalized"], outputs=["features"], depends_on=["normalize"])
    def extract_features(self, inputs):
        return {"features": compute_features(inputs["normalized"])}
```

**Step 3: Run the pipeline**

```python
from meandra.orchestration import SchedulingOrchestrator

workflow = build_workflow(
    FeaturePipeline,
    init_args=("/path/to/data.npy",),
    validate=True,
    available_inputs=set(),
)
orchestrator = SchedulingOrchestrator()
result = orchestrator.run(workflow, {})
print(result["features"])
```

## Tutorial 2: Using the Fluent API

The fluent API provides a functional approach to workflow definition.

```python
from meandra.api import step, pipe

def load_data(inputs):
    return {"data": [1, 2, 3, 4, 5]}

def double(inputs):
    return {"doubled": [x * 2 for x in inputs["data"]]}

def sum_all(inputs):
    return {"total": sum(inputs["doubled"])}

workflow = (
    pipe("calculation")
    .add(step(load_data).out("data"))
    .add(step(double).in_("data").out("doubled").depends_on("load_data"))
    .add(step(sum_all).in_("doubled").out("total").depends_on("double"))
    .build()
)
```

## Tutorial 3: Checkpointing for Long Workflows

Enable checkpointing for fault-tolerant execution.

```python
from meandra.checkpoint import CheckpointManager, FileSystemStorage

@pipeline(name="long_workflow")
class LongWorkflow:
    @node(outputs=["step1"], checkpointable=True)
    def step1(self, inputs):
        # Expensive computation
        return {"step1": expensive_result}

    @node(inputs=["step1"], outputs=["step2"], checkpointable=True, depends_on=["step1"])
    def step2(self, inputs):
        return {"step2": more_computation(inputs["step1"])}

# Create checkpoint manager
storage = FileSystemStorage("/path/to/checkpoints")
manager = CheckpointManager(storage)

# Resume from checkpoint if available
checkpoint = manager.load_latest("long_workflow")
if checkpoint:
    print(f"Resuming from node {checkpoint.node_name}")
```

## Tutorial 4: Validation and Contracts

Use contracts to validate data at node boundaries.

```python
def validate_array(inputs):
    import numpy as np
    assert "data" in inputs, "Missing 'data' input"
    assert isinstance(inputs["data"], np.ndarray), "data must be ndarray"
    assert inputs["data"].ndim >= 1, "data must have at least 1 dimension"

def validate_positive(outputs):
    assert all(v > 0 for v in outputs.values() if isinstance(v, (int, float)))

@pipeline(name="validated")
class ValidatedPipeline:
    @node(
        inputs=["data"],
        outputs=["result"],
        input_contract=validate_array,
        output_contract=validate_positive
    )
    def process(self, inputs):
        return {"result": inputs["data"].sum()}
```
