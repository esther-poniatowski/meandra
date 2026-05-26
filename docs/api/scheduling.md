<a id="scheduling"></a>

# Scheduling

DAG-based dependency resolution for workflow nodes.

<a id="module-meandra.scheduling.scheduler"></a>

<a id="scheduler"></a>

## Scheduler

<a id="meandra-scheduling-scheduler"></a>

### meandra.scheduling.scheduler

Workflow scheduling and dependency resolution.

<a id="meandra.scheduling.scheduler.Scheduler"></a>

### *class* meandra.scheduling.scheduler.Scheduler

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for scheduling tasks within a workflow.

A scheduler determines the execution order of nodes based on their
dependencies, ensuring that all prerequisites are satisfied before
a node executes.

<a id="meandra.scheduling.scheduler.Scheduler.resolve"></a>

#### *abstractmethod* resolve(workflow)

Resolve node dependencies and return execution layers.

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to schedule.
* **Returns:**
  Nodes grouped by execution layer. Nodes within the same layer
  can execute in parallel.
* **Return type:**
  List[List[[Node](core.md#meandra.core.node.Node)]]

<a id="meandra.scheduling.scheduler.DAGScheduler"></a>

### *class* meandra.scheduling.scheduler.DAGScheduler

Bases: [`Scheduler`](#meandra.scheduling.scheduler.Scheduler)

Schedule workflow execution using topological sort.

Uses Kahn’s algorithm to resolve dependencies and group nodes into
execution layers. Nodes within the same layer have no dependencies
on each other and can execute concurrently.

### Notes

The scheduler detects circular dependencies and raises
DependencyResolutionError if found.

### Examples

```pycon
>>> scheduler = DAGScheduler()
>>> layers = scheduler.resolve(workflow)
>>> for i, layer in enumerate(layers):
...     print(f"Layer {i}: {[n.name for n in layer]}")
```

<a id="meandra.scheduling.scheduler.DAGScheduler.resolve"></a>

#### resolve(workflow)

Resolve node dependencies using Kahn’s algorithm.

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to schedule.
* **Returns:**
  Execution layers (parallelizable groups).
* **Return type:**
  List[List[[Node](core.md#meandra.core.node.Node)]]
* **Raises:**
  * [**DependencyResolutionError**](core.md#meandra.core.errors.DependencyResolutionError) – If the workflow contains circular dependencies.
  * [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If a dependency references a non-existent node.

<a id="meandra.scheduling.scheduler.DAGScheduler.get_execution_order"></a>

#### get_execution_order(workflow)

Get a flat execution order (sequential).

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to schedule.
* **Returns:**
  Nodes in valid execution order.
* **Return type:**
  List[[Node](core.md#meandra.core.node.Node)]
