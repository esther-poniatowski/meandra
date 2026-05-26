<a id="monitoring"></a>

# Monitoring

Progress tracking, retry utilities, and node execution state tracking.

<a id="module-meandra.monitoring.progress"></a>

<a id="progress"></a>

## Progress

<a id="meandra-monitoring-progress"></a>

### meandra.monitoring.progress

Progress tracking for workflow execution.

<a id="meandra.monitoring.progress.NodeProgress"></a>

### *class* meandra.monitoring.progress.NodeProgress(name, status=NodeState.PENDING, start_time=None, end_time=None, error=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Progress information for a single node.

<a id="meandra.monitoring.progress.NodeProgress.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the node.

<a id="meandra.monitoring.progress.NodeProgress.status"></a>

#### status *: [NodeState](#meandra.monitoring.state_tracker.NodeState)* *= 'pending'*

Current execution status of the node.

<a id="meandra.monitoring.progress.NodeProgress.start_time"></a>

#### start_time *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Timestamp when the node started executing.

<a id="meandra.monitoring.progress.NodeProgress.end_time"></a>

#### end_time *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Timestamp when the node finished executing.

<a id="meandra.monitoring.progress.NodeProgress.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Error message if the node failed.

<a id="meandra.monitoring.progress.NodeProgress.duration_seconds"></a>

#### *property* duration_seconds *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)*

Return execution duration in seconds, if completed.

* **Returns:**
  Duration in seconds, or None if the node has not started.
* **Return type:**
  [float](https://docs.python.org/3/library/functions.html#float) or None

<a id="meandra.monitoring.progress.ProgressTracker"></a>

### *class* meandra.monitoring.progress.ProgressTracker(workflow_name, total_nodes, nodes=<factory>, callbacks=<factory>, start_time=None, end_time=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Track progress of workflow execution.

Provides real-time visibility into workflow execution state,
including node status, timing, and completion percentage.

### Examples

```pycon
>>> tracker = ProgressTracker("my_workflow", 5)
>>> tracker.add_callback(lambda t: print(f"Progress: {t.percentage:.0f}%"))
>>> tracker.start_node("load_data")
>>> tracker.complete_node("load_data", {"data": [1, 2, 3]})
Progress: 20%
```

<a id="meandra.monitoring.progress.ProgressTracker.workflow_name"></a>

#### workflow_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the workflow being tracked.

<a id="meandra.monitoring.progress.ProgressTracker.total_nodes"></a>

#### total_nodes *: [int](https://docs.python.org/3/library/functions.html#int)*

Total number of nodes in the workflow.

<a id="meandra.monitoring.progress.ProgressTracker.nodes"></a>

#### nodes *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [NodeProgress](#meandra.monitoring.progress.NodeProgress)]*

<a id="meandra.monitoring.progress.ProgressTracker.callbacks"></a>

#### callbacks *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[ProgressTracker](#meandra.monitoring.progress.ProgressTracker)], [None](https://docs.python.org/3/library/constants.html#None)]]*

Functions to call on progress updates.

<a id="meandra.monitoring.progress.ProgressTracker.start_time"></a>

#### start_time *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="meandra.monitoring.progress.ProgressTracker.end_time"></a>

#### end_time *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="meandra.monitoring.progress.ProgressTracker.completed_count"></a>

#### *property* completed_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Return number of completed nodes.

* **Returns:**
  Count of nodes with completed or skipped status.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="meandra.monitoring.progress.ProgressTracker.failed_count"></a>

#### *property* failed_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Return number of failed nodes.

* **Returns:**
  Count of nodes with failed status.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="meandra.monitoring.progress.ProgressTracker.running_count"></a>

#### *property* running_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Return number of currently running nodes.

* **Returns:**
  Count of nodes with running status.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="meandra.monitoring.progress.ProgressTracker.percentage"></a>

#### *property* percentage *: [float](https://docs.python.org/3/library/functions.html#float)*

Return completion percentage (0-100).

* **Returns:**
  Completion percentage from 0 to 100.
* **Return type:**
  [float](https://docs.python.org/3/library/functions.html#float)

<a id="meandra.monitoring.progress.ProgressTracker.elapsed_seconds"></a>

#### *property* elapsed_seconds *: [float](https://docs.python.org/3/library/functions.html#float)*

Return elapsed time since start in seconds.

* **Returns:**
  Elapsed time in seconds since the workflow started.
* **Return type:**
  [float](https://docs.python.org/3/library/functions.html#float)

<a id="meandra.monitoring.progress.ProgressTracker.is_complete"></a>

#### *property* is_complete *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Return True if all nodes have been processed.

* **Returns:**
  True if all nodes are completed or failed.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.monitoring.progress.ProgressTracker.add_callback"></a>

#### add_callback(callback)

Register a callback to be called on progress updates.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*ProgressTracker*](#meandra.monitoring.progress.ProgressTracker) *]* *,* *None* *]*) – Function to invoke on each progress update.

<a id="meandra.monitoring.progress.ProgressTracker.remove_callback"></a>

#### remove_callback(callback)

Remove a registered callback.

* **Parameters:**
  **callback** (*Callable* *[* *[*[*ProgressTracker*](#meandra.monitoring.progress.ProgressTracker) *]* *,* *None* *]*) – Function to remove from the callback list.

<a id="meandra.monitoring.progress.ProgressTracker.start_node"></a>

#### start_node(node_name)

Mark a node as running.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to start.

<a id="meandra.monitoring.progress.ProgressTracker.complete_node"></a>

#### complete_node(node_name, outputs=None)

Mark a node as completed.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark as completed.
  * **outputs** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]*) – Output values produced by the node.

<a id="meandra.monitoring.progress.ProgressTracker.fail_node"></a>

#### fail_node(node_name, error)

Mark a node as failed.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark as failed.
  * **error** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Error message describing the failure.

<a id="meandra.monitoring.progress.ProgressTracker.skip_node"></a>

#### skip_node(node_name)

Mark a node as skipped.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark as skipped.

<a id="meandra.monitoring.progress.ProgressTracker.finish"></a>

#### finish()

Mark the workflow as finished.

<a id="meandra.monitoring.progress.ProgressTracker.to_dict"></a>

#### to_dict()

Convert progress state to a dictionary.

* **Returns:**
  Serialized progress state including node details.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.monitoring.progress.ProgressTracker.summary"></a>

#### summary()

Return a human-readable summary string.

* **Returns:**
  Formatted summary of workflow progress.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="module-meandra.monitoring.retry"></a>

<a id="retry"></a>

## Retry

<a id="meandra-monitoring-retry"></a>

### meandra.monitoring.retry

Retry utilities with exponential backoff.

<a id="meandra.monitoring.retry.RetryConfig"></a>

### *class* meandra.monitoring.retry.RetryConfig(max_attempts=3, base_delay=1.0, max_delay=60.0, exponential_base=2.0, jitter=True, retryable_exceptions=(<class 'Exception'>, ))

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Configuration for retry behavior.

<a id="meandra.monitoring.retry.RetryConfig.max_attempts"></a>

#### max_attempts *: [int](https://docs.python.org/3/library/functions.html#int)* *= 3*

Maximum number of attempts (including initial attempt).

<a id="meandra.monitoring.retry.RetryConfig.base_delay"></a>

#### base_delay *: [float](https://docs.python.org/3/library/functions.html#float)* *= 1.0*

Initial delay between retries in seconds.

<a id="meandra.monitoring.retry.RetryConfig.max_delay"></a>

#### max_delay *: [float](https://docs.python.org/3/library/functions.html#float)* *= 60.0*

Maximum delay between retries in seconds.

<a id="meandra.monitoring.retry.RetryConfig.exponential_base"></a>

#### exponential_base *: [float](https://docs.python.org/3/library/functions.html#float)* *= 2.0*

Base for exponential backoff calculation.

<a id="meandra.monitoring.retry.RetryConfig.jitter"></a>

#### jitter *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= True*

Whether to add random jitter to delays.

<a id="meandra.monitoring.retry.RetryConfig.retryable_exceptions"></a>

#### retryable_exceptions *: [Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple)[[Type](https://docs.python.org/3/library/typing.html#typing.Type)[[Exception](https://docs.python.org/3/library/exceptions.html#Exception)], ...]* *= (<class 'Exception'>,)*

Exception types that should trigger a retry.

<a id="meandra.monitoring.retry.RetryConfig.calculate_delay"></a>

#### calculate_delay(attempt)

Calculate delay for the given attempt number.

Uses exponential backoff with optional jitter.

* **Parameters:**
  **attempt** ([*int*](https://docs.python.org/3/library/functions.html#int)) – The attempt number (1-indexed).
* **Returns:**
  Delay in seconds before next attempt.
* **Return type:**
  [float](https://docs.python.org/3/library/functions.html#float)

<a id="meandra.monitoring.retry.retry"></a>

### meandra.monitoring.retry.retry(max_attempts=3, base_delay=1.0, max_delay=60.0, exponential_base=2.0, jitter=True, retryable_exceptions=(<class 'Exception'>, ), on_retry=None)

Decorator that retries a function with exponential backoff.

* **Parameters:**
  * **max_attempts** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Maximum number of attempts (including initial attempt). Default 3.
  * **base_delay** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Initial delay between retries in seconds. Default 1.0.
  * **max_delay** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Maximum delay between retries in seconds. Default 60.0.
  * **exponential_base** ([*float*](https://docs.python.org/3/library/functions.html#float)) – Base for exponential backoff calculation. Default 2.0.
  * **jitter** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to add random jitter to delays. Default True.
  * **retryable_exceptions** (*Tuple* *[**Type* *[*[*Exception*](https://docs.python.org/3/library/exceptions.html#Exception) *]* *,*  *...* *]*) – Exception types that should trigger a retry. Default `(Exception,)`.
  * **on_retry** (*Optional* *[**Callable* *[* *[*[*int*](https://docs.python.org/3/library/functions.html#int) *,* [*Exception*](https://docs.python.org/3/library/exceptions.html#Exception) *,* [*float*](https://docs.python.org/3/library/functions.html#float) *]* *,* *None* *]* *]*) – Callback called before each retry with (attempt, exception, delay).
* **Returns:**
  Decorated function with retry behavior.
* **Return type:**
  Callable[[Callable[…, T]], Callable[…, T]]

### Examples

```pycon
>>> @retry(max_attempts=3, base_delay=0.1)
... def flaky_operation():
...     # May fail intermittently
...     pass
```

```pycon
>>> @retry(retryable_exceptions=(ConnectionError, TimeoutError))
... def network_call():
...     # Only retry on connection/timeout errors
...     pass
```

<a id="meandra.monitoring.retry.execute_with_retry"></a>

### meandra.monitoring.retry.execute_with_retry(func, config, on_retry=None, \*args, \*\*kwargs)

Execute a function with retry logic.

* **Parameters:**
  * **func** (*Callable* *[* *...* *,* *T* *]*) – Function to execute.
  * **config** ([*RetryConfig*](#meandra.monitoring.retry.RetryConfig)) – Retry configuration.
  * **on_retry** (*Optional* *[**Callable* *[* *[*[*int*](https://docs.python.org/3/library/functions.html#int) *,* [*Exception*](https://docs.python.org/3/library/exceptions.html#Exception) *,* [*float*](https://docs.python.org/3/library/functions.html#float) *]* *,* *None* *]* *]*) – Callback called before each retry.
  * **\*args** (*Any*) – Positional arguments to pass to the function.
  * **\*\*kwargs** (*Any*) – Keyword arguments to pass to the function.
* **Returns:**
  Return value of the function.
* **Return type:**
  T
* **Raises:**
  * [**RetryExhaustedError**](core.md#meandra.core.errors.RetryExhaustedError) – If all retry attempts are exhausted.
  * [**Exception**](https://docs.python.org/3/library/exceptions.html#Exception) – If a non-retryable exception is raised.

<a id="meandra.monitoring.retry.RetryContext"></a>

### *class* meandra.monitoring.retry.RetryContext(config)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Context manager for retryable code blocks.

* **Parameters:**
  **config** ([*RetryConfig*](#meandra.monitoring.retry.RetryConfig)) – Retry configuration governing attempts and delays.

### Examples

```pycon
>>> config = RetryConfig(max_attempts=3)
>>> with RetryContext(config) as ctx:
...     for attempt in ctx:
...         try:
...             result = risky_operation()
...             break  # Success
...         except Exception as e:
...             ctx.record_failure(e)
```

<a id="meandra.monitoring.retry.RetryContext.record_failure"></a>

#### record_failure(error)

Record a failure and wait before next attempt.

* **Parameters:**
  **error** ([*Exception*](https://docs.python.org/3/library/exceptions.html#Exception)) – The exception that caused the failure.

<a id="module-meandra.monitoring.state_tracker"></a>

<a id="state-tracker"></a>

## State Tracker

<a id="meandra-monitoring-state-tracker"></a>

### meandra.monitoring.state_tracker

Track workflow and node execution state.

<a id="meandra.monitoring.state_tracker.NodeState"></a>

### *class* meandra.monitoring.state_tracker.NodeState(\*values)

Bases: [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Possible states for a node during execution.

<a id="meandra.monitoring.state_tracker.NodeState.PENDING"></a>

#### PENDING *= 'pending'*

<a id="meandra.monitoring.state_tracker.NodeState.RUNNING"></a>

#### RUNNING *= 'running'*

<a id="meandra.monitoring.state_tracker.NodeState.COMPLETED"></a>

#### COMPLETED *= 'completed'*

<a id="meandra.monitoring.state_tracker.NodeState.FAILED"></a>

#### FAILED *= 'failed'*

<a id="meandra.monitoring.state_tracker.NodeState.SKIPPED"></a>

#### SKIPPED *= 'skipped'*

<a id="meandra.monitoring.state_tracker.NodeExecution"></a>

### *class* meandra.monitoring.state_tracker.NodeExecution(node_name, state=NodeState.PENDING, start_time=None, end_time=None, error=None, outputs=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Record of a node execution.

<a id="meandra.monitoring.state_tracker.NodeExecution.node_name"></a>

#### node_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the executed node.

<a id="meandra.monitoring.state_tracker.NodeExecution.state"></a>

#### state *: [NodeState](#meandra.monitoring.state_tracker.NodeState)* *= 'pending'*

Current state of the node.

<a id="meandra.monitoring.state_tracker.NodeExecution.start_time"></a>

#### start_time *: [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Timestamp when execution started.

<a id="meandra.monitoring.state_tracker.NodeExecution.end_time"></a>

#### end_time *: [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Timestamp when execution ended.

<a id="meandra.monitoring.state_tracker.NodeExecution.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Error message if the node failed.

<a id="meandra.monitoring.state_tracker.NodeExecution.outputs"></a>

#### outputs *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Output data produced by the node.

<a id="meandra.monitoring.state_tracker.StateTracker"></a>

### *class* meandra.monitoring.state_tracker.StateTracker

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for tracking workflow execution state.

Tracks the execution state of each node and provides logging
and recovery capabilities.

<a id="meandra.monitoring.state_tracker.StateTracker.mark_running"></a>

#### *abstractmethod* mark_running(node_name)

Mark a node as running.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.StateTracker.mark_completed"></a>

#### *abstractmethod* mark_completed(node_name, outputs)

Mark a node as completed with outputs.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **outputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Output data produced by the node.

<a id="meandra.monitoring.state_tracker.StateTracker.mark_failed"></a>

#### *abstractmethod* mark_failed(node_name, error)

Mark a node as failed with error message.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **error** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Error message describing the failure.

<a id="meandra.monitoring.state_tracker.StateTracker.mark_skipped"></a>

#### *abstractmethod* mark_skipped(node_name)

Mark a node as skipped.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.StateTracker.get_state"></a>

#### *abstractmethod* get_state(node_name)

Get the current state of a node.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to query.
* **Returns:**
  Current state of the node.
* **Return type:**
  [NodeState](#meandra.monitoring.state_tracker.NodeState)

<a id="meandra.monitoring.state_tracker.StateTracker.is_completed"></a>

#### *abstractmethod* is_completed(node_name)

Check if a node has completed successfully.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to check.
* **Returns:**
  True if the node completed successfully.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.monitoring.state_tracker.StateTracker.get_completed_nodes"></a>

#### *abstractmethod* get_completed_nodes()

Get list of completed node names.

* **Returns:**
  Names of all completed nodes.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker"></a>

### *class* meandra.monitoring.state_tracker.InMemoryStateTracker(workflow_name, run_id)

Bases: [`StateTracker`](#meandra.monitoring.state_tracker.StateTracker)

Track execution state in memory.

Suitable for single-run workflows where persistence is not needed.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow being tracked.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique identifier for the current run.

### Examples

```pycon
>>> tracker = InMemoryStateTracker("my_workflow", "run_001")
>>> tracker.mark_running("node_a")
>>> tracker.get_state("node_a")
<NodeState.RUNNING: 'running'>
```

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.executions"></a>

#### executions *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [NodeExecution](#meandra.monitoring.state_tracker.NodeExecution)]*

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.mark_running"></a>

#### mark_running(node_name)

Mark a node as running.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.mark_completed"></a>

#### mark_completed(node_name, outputs)

Mark a node as completed with outputs.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **outputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Output data produced by the node.

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.mark_failed"></a>

#### mark_failed(node_name, error)

Mark a node as failed with error message.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **error** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Error message describing the failure.

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.mark_skipped"></a>

#### mark_skipped(node_name)

Mark a node as skipped.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.get_state"></a>

#### get_state(node_name)

Get the current state of a node.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to query.
* **Returns:**
  Current state of the node.
* **Return type:**
  [NodeState](#meandra.monitoring.state_tracker.NodeState)

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.is_completed"></a>

#### is_completed(node_name)

Check if a node has completed successfully.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to check.
* **Returns:**
  True if the node completed successfully.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.get_completed_nodes"></a>

#### get_completed_nodes()

Get list of completed node names.

* **Returns:**
  Names of all completed nodes.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.get_failed_nodes"></a>

#### get_failed_nodes()

Get list of failed node names.

* **Returns:**
  Names of all failed nodes.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.get_outputs"></a>

#### get_outputs(node_name)

Get outputs from a completed node.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to query.
* **Returns:**
  Output data from the node, or None if not found.
* **Return type:**
  Optional[Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]]

<a id="meandra.monitoring.state_tracker.InMemoryStateTracker.summary"></a>

#### summary()

Get summary of execution state.

* **Returns:**
  Dictionary with run metadata and counts.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.monitoring.state_tracker.FileStateTracker"></a>

### *class* meandra.monitoring.state_tracker.FileStateTracker(workflow_name, run_id, path)

Bases: [`StateTracker`](#meandra.monitoring.state_tracker.StateTracker)

Persist execution state as JSON lines with query support.

Each state change is appended to a log file. Query methods parse
the log file to reconstruct current state.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow being tracked.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique run identifier.
  * **path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *or* *Path*) – Path to the log file.

### Examples

```pycon
>>> tracker = FileStateTracker("my_workflow", "run_001", "state.jsonl")
>>> tracker.mark_running("node_a")
>>> tracker.mark_completed("node_a", {"result": 42})
>>> tracker.get_state("node_a")
<NodeState.COMPLETED: 'completed'>
```

<a id="meandra.monitoring.state_tracker.FileStateTracker.mark_running"></a>

#### mark_running(node_name)

Mark a node as running.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.FileStateTracker.mark_completed"></a>

#### mark_completed(node_name, outputs)

Mark a node as completed with outputs.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **outputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Output data produced by the node.

<a id="meandra.monitoring.state_tracker.FileStateTracker.mark_failed"></a>

#### mark_failed(node_name, error)

Mark a node as failed with error message.

* **Parameters:**
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.
  * **error** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Error message describing the failure.

<a id="meandra.monitoring.state_tracker.FileStateTracker.mark_skipped"></a>

#### mark_skipped(node_name)

Mark a node as skipped.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to mark.

<a id="meandra.monitoring.state_tracker.FileStateTracker.get_state"></a>

#### get_state(node_name)

Get the current state of a node.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to query.
* **Returns:**
  Current state of the node.
* **Return type:**
  [NodeState](#meandra.monitoring.state_tracker.NodeState)

<a id="meandra.monitoring.state_tracker.FileStateTracker.is_completed"></a>

#### is_completed(node_name)

Check if a node has completed successfully.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node to check.
* **Returns:**
  True if the node completed successfully.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.monitoring.state_tracker.FileStateTracker.get_completed_nodes"></a>

#### get_completed_nodes()

Get list of completed node names.

* **Returns:**
  Names of all completed nodes.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.monitoring.state_tracker.FileStateTracker.get_failed_nodes"></a>

#### get_failed_nodes()

Get list of failed node names.

* **Returns:**
  Names of all failed nodes.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]
