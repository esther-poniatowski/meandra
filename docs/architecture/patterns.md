# Design Patterns

This document describes the design patterns used in Meandra.

## Builder Pattern

Both the decorator and fluent APIs use the builder pattern:

**Fluent API Builder**:

```python
workflow = (
    pipe("name")
    .add(step(func1).out("a"))
    .add(step(func2).in_("a").out("b"))
    .build()
)
```

**Decorator API Builder**:

```python
@pipeline(name="name")
class MyPipeline:
    @node(outputs=["a"])
    def step1(self, inputs): ...

workflow = build_workflow(MyPipeline)
```

Benefits:

- Fluent, readable API
- Configuration validation at build time
- Immutable products

## Strategy Pattern

The orchestrator uses the strategy pattern for scheduling:

```python
class Orchestrator(ABC):
    @abstractmethod
    def run(self, workflow, inputs): ...

class SchedulingOrchestrator(Orchestrator):
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
```

The strategy pattern allows different scheduling policies without changing orchestration logic.

## Template Method Pattern

The `Node` execution follows a template method pattern:

1. Validate inputs (via `input_contract`)
2. Execute function
3. Validate outputs (via `output_contract`)
4. Return results

Subclasses can override specific steps through contracts.

## Observer Pattern

Progress tracking uses the observer pattern:

```python
tracker = ProgressTracker("workflow", total_nodes=5)
tracker.add_callback(lambda t: print(t.percentage))
tracker.complete_node("step1")  # Callbacks notified
```

The observer pattern decouples progress reporting from execution logic.

## Registry Pattern

The `DataCatalog` uses a registry pattern:

```python
catalog = DataCatalog()
catalog.register("dataset1", "/path/to/data.npy")
catalog.register("dataset2", "/path/to/other.pkl")

data = catalog.load("dataset1")
```

Benefits:

- Centralized resource management
- Lazy loading
- Path abstraction

## Decorator Pattern

The `@node` and `@pipeline` decorators add metadata without modifying behavior:

```python
@node(outputs=["data"])
def load_data(inputs):
    return {"data": [1, 2, 3]}

# Function still callable normally
result = load_data({})

# But carries node specification
spec = get_node_spec(load_data)
```

The decorator approach allows gradual adoption and testing without the framework.

## Context Manager Pattern

Retry operations support context manager usage:

```python
config = RetryConfig(max_attempts=3)
with RetryContext(config) as ctx:
    for attempt in ctx:
        try:
            result = risky_operation()
            break
        except Exception as e:
            ctx.record_failure(e)
```

The context manager provides clean resource management and retry logic.
