<a id="orchestration"></a>

# Orchestration

Workflow execution with state tracking and hook events.

<a id="module-meandra.orchestration.orchestrator"></a>

<a id="orchestrator"></a>

## Orchestrator

<a id="meandra-orchestration-orchestrator"></a>

### meandra.orchestration.orchestrator

Workflow execution orchestration.

<a id="meandra.orchestration.orchestrator.HookEvent"></a>

### *class* meandra.orchestration.orchestrator.HookEvent(\*values)

Bases: [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Lifecycle events for workflow execution.

<a id="meandra.orchestration.orchestrator.HookEvent.BEFORE_WORKFLOW"></a>

#### BEFORE_WORKFLOW *= 'before_workflow'*

<a id="meandra.orchestration.orchestrator.HookEvent.AFTER_WORKFLOW"></a>

#### AFTER_WORKFLOW *= 'after_workflow'*

<a id="meandra.orchestration.orchestrator.HookEvent.BEFORE_NODE"></a>

#### BEFORE_NODE *= 'before_node'*

<a id="meandra.orchestration.orchestrator.HookEvent.AFTER_NODE"></a>

#### AFTER_NODE *= 'after_node'*

<a id="meandra.orchestration.orchestrator.HookEvent.ON_ERROR"></a>

#### ON_ERROR *= 'on_error'*

<a id="meandra.orchestration.orchestrator.WorkflowExecutionError"></a>

### *exception* meandra.orchestration.orchestrator.WorkflowExecutionError(message, workflow_name, node_name, original_error)

Bases: [`NodeExecutionError`](core.md#meandra.core.errors.NodeExecutionError)

Raised when workflow execution fails.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error description.
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow that failed.
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node that caused the failure.
  * **original_error** ([*Exception*](https://docs.python.org/3/library/exceptions.html#Exception)) – The underlying exception.

<a id="meandra.orchestration.orchestrator.Orchestrator"></a>

### *class* meandra.orchestration.orchestrator.Orchestrator

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for workflow execution.

An orchestrator controls how a workflow is executed, managing
node ordering, input/output flow, and error handling.

<a id="meandra.orchestration.orchestrator.Orchestrator.run"></a>

#### *abstractmethod* run(workflow, inputs)

Execute a workflow with given inputs.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to execute.
  * **inputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Initial inputs for the workflow.
* **Returns:**
  All outputs from all nodes.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.orchestration.orchestrator.WorkflowState"></a>

### *class* meandra.orchestration.orchestrator.WorkflowState(inputs, artifacts=<factory>, node_outputs=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Explicit runtime state segmented into workflow inputs and produced artifacts.

<a id="meandra.orchestration.orchestrator.WorkflowState.inputs"></a>

#### inputs *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Initial workflow inputs.

<a id="meandra.orchestration.orchestrator.WorkflowState.artifacts"></a>

#### artifacts *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Outputs produced by executed nodes.

<a id="meandra.orchestration.orchestrator.WorkflowState.node_outputs"></a>

#### node_outputs *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]]*

Per-node output mapping.

<a id="meandra.orchestration.orchestrator.WorkflowState.from_resume"></a>

#### *classmethod* from_resume(inputs, snapshot)

Create a state from a checkpoint snapshot merged with new inputs.

* **Parameters:**
  * **inputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – New inputs to overlay on the resumed state.
  * **snapshot** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]*) – Serialized checkpoint containing prior inputs and artifacts.
* **Returns:**
  Reconstituted state ready for resumed execution.
* **Return type:**
  [WorkflowState](#meandra.orchestration.orchestrator.WorkflowState)

<a id="meandra.orchestration.orchestrator.WorkflowState.available_context"></a>

#### available_context()

Return the full context of inputs and artifacts.

* **Returns:**
  Merged mapping of workflow inputs and produced artifacts.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.orchestration.orchestrator.WorkflowState.record_node_outputs"></a>

#### record_node_outputs(node, outputs)

Store outputs produced by a node.

* **Parameters:**
  * **node** ([*Node*](core.md#meandra.core.node.Node)) – The node that produced the outputs.
  * **outputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Mapping of output names to values.

<a id="meandra.orchestration.orchestrator.WorkflowState.snapshot"></a>

#### snapshot()

Serialize the current state for checkpointing.

* **Returns:**
  Mapping with `inputs` and `artifacts` keys.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]]

<a id="meandra.orchestration.orchestrator.InputResolver"></a>

### *class* meandra.orchestration.orchestrator.InputResolver

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Resolve node inputs from the explicit workflow state.

<a id="meandra.orchestration.orchestrator.InputResolver.resolve"></a>

#### resolve(node, workflow, state)

Determine the inputs for a node from the current workflow state.

* **Parameters:**
  * **node** ([*Node*](core.md#meandra.core.node.Node)) – The node whose inputs are being resolved.
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow containing the node.
  * **state** ([*WorkflowState*](#meandra.orchestration.orchestrator.WorkflowState)) – Current runtime state with inputs and artifacts.
* **Returns:**
  Resolved input mapping for the node.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.orchestration.orchestrator.LifecycleEvents"></a>

### *class* meandra.orchestration.orchestrator.LifecycleEvents

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Manage lifecycle hooks separately from execution policy.

<a id="meandra.orchestration.orchestrator.LifecycleEvents.add_hook"></a>

#### add_hook(event, callback)

Register a callback for a lifecycle event.

* **Parameters:**
  * **event** ([*HookEvent*](#meandra.orchestration.orchestrator.HookEvent)) – The event to listen for.
  * **callback** (*Callable* *[* *...* *,* *Any* *]*) – Function to invoke when the event fires.

<a id="meandra.orchestration.orchestrator.LifecycleEvents.remove_hook"></a>

#### remove_hook(event, callback)

Unregister a previously added callback.

* **Parameters:**
  * **event** ([*HookEvent*](#meandra.orchestration.orchestrator.HookEvent)) – The event the callback was registered for.
  * **callback** (*Callable* *[* *...* *,* *Any* *]*) – The callback to remove.

<a id="meandra.orchestration.orchestrator.LifecycleEvents.emit"></a>

#### emit(event, \*args)

Fire all callbacks registered for an event.

* **Parameters:**
  * **event** ([*HookEvent*](#meandra.orchestration.orchestrator.HookEvent)) – The event to emit.
  * **\*args** (*Any*) – Positional arguments forwarded to each callback.

<a id="meandra.orchestration.orchestrator.ResumePolicy"></a>

### *class* meandra.orchestration.orchestrator.ResumePolicy(checkpoint_manager, enabled)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Build explicit resume plans from checkpoint state.

* **Parameters:**
  * **checkpoint_manager** (*Optional* *[*[*CheckpointManager*](checkpoint.md#meandra.checkpoint.manager.CheckpointManager) *]*) – Manager for loading checkpoint data, or `None` to disable.
  * **enabled** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether resume-from-checkpoint is active.

<a id="meandra.orchestration.orchestrator.ResumePolicy.load"></a>

#### load(workflow)

Attempt to load a resume plan for the given workflow.

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to resume.
* **Returns:**
  A resume plan if a valid checkpoint exists, otherwise `None`.
* **Return type:**
  Optional[[ResumePlan](checkpoint.md#meandra.checkpoint.manager.ResumePlan)]

<a id="meandra.orchestration.orchestrator.ExecutionEngine"></a>

### *class* meandra.orchestration.orchestrator.ExecutionEngine(\*, lifecycle, input_resolver, checkpoint_manager, progress_tracker, retry_config, fail_fast, max_workers)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Runtime engine composed from smaller collaborators instead of one sink object.

* **Parameters:**
  * **lifecycle** ([*LifecycleEvents*](#meandra.orchestration.orchestrator.LifecycleEvents)) – Hook manager for workflow lifecycle callbacks.
  * **input_resolver** ([*InputResolver*](#meandra.orchestration.orchestrator.InputResolver)) – Strategy for resolving node inputs from state.
  * **checkpoint_manager** (*Optional* *[*[*CheckpointManager*](checkpoint.md#meandra.checkpoint.manager.CheckpointManager) *]*) – Manager for persisting node checkpoints, or `None`.
  * **progress_tracker** (*Optional* *[*[*ProgressTracker*](monitoring.md#meandra.monitoring.progress.ProgressTracker) *]*) – Tracker for execution progress reporting, or `None`.
  * **retry_config** (*Optional* *[*[*RetryConfig*](monitoring.md#meandra.monitoring.retry.RetryConfig) *]*) – Retry policy for node execution, or `None`.
  * **fail_fast** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If `True`, abort the workflow on the first node failure.
  * **max_workers** (*Optional* *[*[*int*](https://docs.python.org/3/library/functions.html#int) *]*) – Maximum threads for parallel layer execution, or `None` for serial.

<a id="meandra.orchestration.orchestrator.ExecutionEngine.run"></a>

#### run(workflow, layers, inputs, state_tracker, run_id, resume_plan=None)

Execute all layers of a workflow.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow being executed.
  * **layers** (*List* *[**List* *[*[*Node*](core.md#meandra.core.node.Node) *]* *]*) – Topologically sorted layers of nodes.
  * **inputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Initial workflow inputs.
  * **state_tracker** ([*StateTracker*](monitoring.md#meandra.monitoring.state_tracker.StateTracker)) – Tracker for per-node execution state.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique identifier for this execution run.
  * **resume_plan** (*Optional* *[*[*ResumePlan*](checkpoint.md#meandra.checkpoint.manager.ResumePlan) *]*) – Plan describing which nodes to skip on resume, or `None`.
* **Returns:**
  Final state containing all inputs and produced artifacts.
* **Return type:**
  [WorkflowState](#meandra.orchestration.orchestrator.WorkflowState)

<a id="meandra.orchestration.orchestrator.SchedulingOrchestrator"></a>

### *class* meandra.orchestration.orchestrator.SchedulingOrchestrator(scheduler=None, state_tracker=None, checkpoint_manager=None, progress_tracker=None, retry_config=None, fail_fast=True, resume_from_checkpoint=True, max_workers=None)

Bases: [`Orchestrator`](#meandra.orchestration.orchestrator.Orchestrator)

Execute workflows using explicit runtime services and a scheduler.

* **Parameters:**
  * **scheduler** (*Optional* *[*[*Scheduler*](scheduling.md#meandra.scheduling.scheduler.Scheduler) *]*) – Scheduling strategy for node ordering. Defaults to `DAGScheduler`.
  * **state_tracker** (*Optional* *[*[*StateTracker*](monitoring.md#meandra.monitoring.state_tracker.StateTracker) *]*) – Tracker for per-node execution state, or `None` for an in-memory default.
  * **checkpoint_manager** (*Optional* *[*[*CheckpointManager*](checkpoint.md#meandra.checkpoint.manager.CheckpointManager) *]*) – Manager for persisting node checkpoints, or `None`.
  * **progress_tracker** (*Optional* *[*[*ProgressTracker*](monitoring.md#meandra.monitoring.progress.ProgressTracker) *]*) – Tracker for execution progress reporting, or `None`.
  * **retry_config** (*Optional* *[*[*RetryConfig*](monitoring.md#meandra.monitoring.retry.RetryConfig) *]*) – Retry policy for node execution, or `None`.
  * **fail_fast** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If `True`, abort the workflow on the first node failure.
  * **resume_from_checkpoint** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to attempt resuming from the latest checkpoint.
  * **max_workers** (*Optional* *[*[*int*](https://docs.python.org/3/library/functions.html#int) *]*) – Maximum threads for parallel layer execution, or `None` for serial.

<a id="meandra.orchestration.orchestrator.SchedulingOrchestrator.add_hook"></a>

#### add_hook(event, callback)

Register a lifecycle hook callback.

* **Parameters:**
  * **event** ([*HookEvent*](#meandra.orchestration.orchestrator.HookEvent)) – The event to listen for.
  * **callback** (*Callable* *[* *...* *,* *Any* *]*) – Function to invoke when the event fires.

<a id="meandra.orchestration.orchestrator.SchedulingOrchestrator.remove_hook"></a>

#### remove_hook(event, callback)

Unregister a lifecycle hook callback.

* **Parameters:**
  * **event** ([*HookEvent*](#meandra.orchestration.orchestrator.HookEvent)) – The event the callback was registered for.
  * **callback** (*Callable* *[* *...* *,* *Any* *]*) – The callback to remove.

<a id="meandra.orchestration.orchestrator.SchedulingOrchestrator.run"></a>

#### run(workflow, inputs)

Execute a workflow with given inputs.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to execute.
  * **inputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*  *|* [*ConfigProvider*](configuration.md#meandra.configuration.mod.ConfigProvider)) – Initial inputs or a configuration provider to resolve.
* **Returns:**
  All outputs from all nodes.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]
