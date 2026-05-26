<a id="core"></a>

# Core

Fundamental data structures for workflows: nodes, workflows, graphs, and errors.

<a id="module-meandra.core.node"></a>

<a id="node"></a>

## Node

<a id="meandra-core-node"></a>

### meandra.core.node

Processing nodes for workflow execution.

<a id="meandra.core.node.PortSpec"></a>

### *class* meandra.core.node.PortSpec(name)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Explicit description of a workflow input or output port.

<a id="meandra.core.node.PortSpec.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the port.

<a id="meandra.core.node.NodeContract"></a>

### *class* meandra.core.node.NodeContract(inputs=(), outputs=(), accepts_context=False)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Explicit IO contract for a workflow node.

<a id="meandra.core.node.NodeContract.inputs"></a>

#### inputs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PortSpec](#meandra.core.node.PortSpec), ...]* *= ()*

Input port specifications.

<a id="meandra.core.node.NodeContract.outputs"></a>

#### outputs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PortSpec](#meandra.core.node.PortSpec), ...]* *= ()*

Output port specifications.

<a id="meandra.core.node.NodeContract.accepts_context"></a>

#### accepts_context *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the node accepts the full execution context.

<a id="meandra.core.node.NodeContract.input_names"></a>

#### *property* input_names *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Return the names of all input ports.

* **Returns:**
  Names of the input ports.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.core.node.NodeContract.output_names"></a>

#### *property* output_names *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Return the names of all output ports.

* **Returns:**
  Names of the output ports.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.core.node.Node"></a>

### *class* meandra.core.node.Node(name, func, dependencies=<factory>, inputs=<factory>, outputs=<factory>, is_checkpointable=False, accepts_context=False, input_contract=None, output_contract=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Define a processing node in the workflow.

A node represents a single computation step with explicit inputs,
outputs, and dependencies on other nodes.

### Examples

```pycon
>>> def add(inputs):
...     return {"sum": inputs["a"] + inputs["b"]}
>>> node = Node("adder", add, inputs=["a", "b"], outputs=["sum"])
>>> result = node.execute({"a": 1, "b": 2})
>>> result
{'sum': 3}
```

<a id="meandra.core.node.Node.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique identifier for the node within a workflow.

<a id="meandra.core.node.Node.func"></a>

#### func *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Function to execute. Takes a dict of inputs and returns outputs.

<a id="meandra.core.node.Node.dependencies"></a>

#### dependencies *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Names of nodes this node depends on (outputs needed as inputs).

<a id="meandra.core.node.Node.inputs"></a>

#### inputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Names of input keys expected from dependencies or workflow inputs.

<a id="meandra.core.node.Node.outputs"></a>

#### outputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Names of output keys produced by this node.

<a id="meandra.core.node.Node.is_checkpointable"></a>

#### is_checkpointable *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether node outputs should be checkpointed.

<a id="meandra.core.node.Node.accepts_context"></a>

#### accepts_context *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

If True, the node receives the full context when inputs are not specified.

<a id="meandra.core.node.Node.input_contract"></a>

#### input_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Optional validator for node inputs.

<a id="meandra.core.node.Node.output_contract"></a>

#### output_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Optional validator for node outputs.

<a id="meandra.core.node.Node.contract"></a>

#### *property* contract *: [NodeContract](#meandra.core.node.NodeContract)*

Return the structured contract shared by validation, CLI, and execution layers.

* **Returns:**
  IO contract describing the node’s input and output ports.
* **Return type:**
  [NodeContract](#meandra.core.node.NodeContract)

<a id="meandra.core.node.Node.execute"></a>

#### execute(inputs)

Execute the node function with the provided inputs.

* **Parameters:**
  **inputs** (*Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]*) – Input data for the node.
* **Returns:**
  Output data produced by the node.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.core.node.Node.clone"></a>

#### clone(\*\*changes)

Create a modified copy without reconstructing the node field-by-field.

* **Parameters:**
  **\*\*changes** (*Any*) – Field values to override in the cloned node.
* **Returns:**
  New node with the specified changes applied.
* **Return type:**
  [Node](#meandra.core.node.Node)

<a id="module-meandra.core.workflow"></a>

<a id="workflow"></a>

## Workflow

<a id="meandra-core-workflow"></a>

### meandra.core.workflow

Workflow definition and management.

<a id="meandra.core.workflow.ValidationResult"></a>

### *class* meandra.core.workflow.ValidationResult(valid, errors=<factory>, warnings=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Result of workflow validation.

<a id="meandra.core.workflow.ValidationResult.valid"></a>

#### valid *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Whether the workflow passed validation.

<a id="meandra.core.workflow.ValidationResult.errors"></a>

#### errors *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Validation errors found.

<a id="meandra.core.workflow.ValidationResult.warnings"></a>

#### warnings *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Validation warnings found.

<a id="meandra.core.workflow.ValidationResult.raise_if_invalid"></a>

#### raise_if_invalid(workflow_name='')

Raise ValidationError if validation failed.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow for the error message.

<a id="meandra.core.workflow.Workflow"></a>

### *class* meandra.core.workflow.Workflow(name, nodes=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Define a workflow composed of multiple processing nodes.

A workflow is a directed acyclic graph (DAG) of nodes, where each node
represents a computation step with explicit dependencies.

### Examples

```pycon
>>> def load_data(inputs):
...     return {"data": [1, 2, 3]}
>>> def process(inputs):
...     return {"result": sum(inputs["data"])}
>>> wf = Workflow("example")
>>> wf.add_node(Node("loader", load_data, outputs=["data"]))
>>> wf.add_node(Node("processor", process, dependencies=["loader"], inputs=["data"], outputs=["result"]))
```

<a id="meandra.core.workflow.Workflow.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique identifier for the workflow.

<a id="meandra.core.workflow.Workflow.nodes"></a>

#### nodes *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Node](#meandra.core.node.Node)]*

Mapping of node names to Node instances.

<a id="meandra.core.workflow.Workflow.add_node"></a>

#### add_node(node)

Register a node in the workflow.

* **Parameters:**
  **node** ([*Node*](#meandra.core.node.Node)) – Node to add to the workflow.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If a node with the same name already exists.

<a id="meandra.core.workflow.Workflow.get_node"></a>

#### get_node(name)

Get a node by name.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node.
* **Returns:**
  The requested node.
* **Return type:**
  [Node](#meandra.core.node.Node)
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If node does not exist.

<a id="meandra.core.workflow.Workflow.validate"></a>

#### validate(available_inputs=None)

Validate the workflow structure.

Checks for:
- Missing dependencies (nodes that reference non-existent nodes)
- Cyclic dependencies
- Unsatisfiable inputs (inputs not provided by dependencies or available_inputs)

* **Parameters:**
  **available_inputs** (*Optional* *[**Set* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Set of input keys that will be provided at execution time.
  If None, input satisfiability is not checked.
* **Returns:**
  Validation result with errors and warnings.
* **Return type:**
  [ValidationResult](#meandra.core.workflow.ValidationResult)

### Examples

```pycon
>>> wf = Workflow("test")
>>> wf.add_node(Node("a", func, outputs=["x"]))
>>> wf.add_node(Node("b", func, dependencies=["a"], inputs=["x"]))
>>> result = wf.validate()
>>> result.valid
True
```

<a id="meandra.core.workflow.Workflow.structure_hash"></a>

#### structure_hash()

Compute a stable hash of the workflow structure.

Includes node names, dependencies, inputs, outputs, and flags.

* **Returns:**
  SHA-256 hex digest of the workflow structure.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="meandra.core.workflow.Workflow.build_model"></a>

#### build_model()

Build a canonical workflow model for execution and inspection.

* **Returns:**
  Canonical representation of nodes, edges, and IO keys.
* **Return type:**
  [WorkflowModel](#meandra.core.workflow.WorkflowModel)

<a id="meandra.core.workflow.Workflow.required_inputs"></a>

#### required_inputs()

Return workflow inputs that must come from outside the workflow.

* **Returns:**
  Input keys not produced by any node in the workflow.
* **Return type:**
  Set[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.core.workflow.Workflow.clone_with_nodes"></a>

#### clone_with_nodes(nodes)

Create a workflow copy from a new node collection.

* **Parameters:**
  **nodes** (*List* *[*[*Node*](#meandra.core.node.Node) *]*) – Nodes to include in the cloned workflow.
* **Returns:**
  New workflow with the given nodes.
* **Return type:**
  [Workflow](#meandra.core.workflow.Workflow)

<a id="meandra.core.workflow.Workflow.transform_nodes"></a>

#### transform_nodes(transformer)

Apply a node transformer across the workflow through a stable extension seam.

* **Parameters:**
  **transformer** (*Callable* *[* *[*[*Node*](#meandra.core.node.Node) *]* *,* [*Node*](#meandra.core.node.Node) *]*) – Function that transforms a node into a new node.
* **Returns:**
  New workflow with transformed nodes.
* **Return type:**
  [Workflow](#meandra.core.workflow.Workflow)

<a id="meandra.core.workflow.WorkflowModel"></a>

### *class* meandra.core.workflow.WorkflowModel(name, nodes, edges, inputs, outputs)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Canonical workflow representation.

<a id="meandra.core.workflow.WorkflowModel.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Workflow name.

<a id="meandra.core.workflow.WorkflowModel.nodes"></a>

#### nodes *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[Node](#meandra.core.node.Node)]*

Nodes in the workflow.

<a id="meandra.core.workflow.WorkflowModel.edges"></a>

#### edges *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]]*

Directed edges as (dependency, dependent).

<a id="meandra.core.workflow.WorkflowModel.inputs"></a>

#### inputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Unique input keys expected by nodes.

<a id="meandra.core.workflow.WorkflowModel.outputs"></a>

#### outputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Unique output keys produced by nodes.

<a id="module-meandra.core.graph"></a>

<a id="graph"></a>

## Graph

<a id="meandra-core-graph"></a>

### meandra.core.graph

Graph algorithms shared across the framework.

<a id="meandra.core.graph.topological_layers"></a>

### meandra.core.graph.topological_layers(nodes, dependencies)

Compute a layered topological ordering using Kahn’s algorithm.

Nodes within the same layer have no mutual dependencies and can be
processed concurrently.

* **Parameters:**
  * **nodes** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *T* *]*) – Mapping of node name to node object.
  * **dependencies** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Sequence* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Mapping of node name to the names it depends on.
    Every dependency name must exist as a key in *nodes*.
* **Returns:**
  Nodes grouped into execution layers.  The first layer contains
  nodes with no dependencies; subsequent layers contain nodes
  whose dependencies all appear in earlier layers.
* **Return type:**
  List[List[T]]
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If a dependency references a name not present in *nodes*.

### Notes

If the graph contains a cycle, the returned layers will be
incomplete (fewer total items than `len(nodes)`).  Callers are
responsible for detecting this condition and raising an appropriate
error.

<a id="module-meandra.core.errors"></a>

<a id="errors"></a>

## Errors

<a id="meandra-core-errors"></a>

### meandra.core.errors

Custom exception hierarchy for Meandra.

All Meandra-specific exceptions inherit from MeandraError, enabling
unified error handling across the framework.

<a id="meandra.core.errors.MeandraError"></a>

### *exception* meandra.core.errors.MeandraError(message, \*\*details)

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Base exception for all Meandra errors.

All Meandra-specific exceptions inherit from this class, enabling
unified error handling and structured error information.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.MeandraError.to_dict"></a>

#### to_dict()

Convert exception to a dictionary for structured logging.

* **Returns:**
  Structured error representation.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.core.errors.WorkflowError"></a>

### *exception* meandra.core.errors.WorkflowError(message, workflow_name, \*\*details)

Bases: [`MeandraError`](#meandra.core.errors.MeandraError)

Base exception for workflow-related errors.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow that encountered the error.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.NodeExecutionError"></a>

### *exception* meandra.core.errors.NodeExecutionError(message, workflow_name, node_name, original_error=None, \*\*details)

Bases: [`WorkflowError`](#meandra.core.errors.WorkflowError)

Raised when a node fails during execution.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow that encountered the error.
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node that failed.
  * **original_error** (*Optional* *[*[*Exception*](https://docs.python.org/3/library/exceptions.html#Exception) *]*) – The underlying exception that caused the failure.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.NodeExecutionError.to_dict"></a>

#### to_dict()

Convert exception to a dictionary for structured logging.

* **Returns:**
  Structured error representation.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.core.errors.DependencyResolutionError"></a>

### *exception* meandra.core.errors.DependencyResolutionError(message, workflow_name, cycle=None, missing=None, \*\*details)

Bases: [`WorkflowError`](#meandra.core.errors.WorkflowError)

Raised when workflow dependencies cannot be resolved.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow that encountered the error.
  * **cycle** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – List of node names involved in a dependency cycle, if applicable.
  * **missing** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – List of missing dependency names, if applicable.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.DependencyResolutionError.to_dict"></a>

#### to_dict()

Convert exception to a dictionary for structured logging.

* **Returns:**
  Structured error representation.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.core.errors.ValidationError"></a>

### *exception* meandra.core.errors.ValidationError(message, workflow_name, errors=None, warnings=None, \*\*details)

Bases: [`WorkflowError`](#meandra.core.errors.WorkflowError)

Raised when workflow validation fails.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow that encountered the error.
  * **errors** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – List of validation error messages.
  * **warnings** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – List of validation warning messages.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.ValidationError.to_dict"></a>

#### to_dict()

Convert exception to a dictionary for structured logging.

* **Returns:**
  Structured error representation.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.core.errors.CheckpointError"></a>

### *exception* meandra.core.errors.CheckpointError(message, operation, checkpoint_id=None, \*\*details)

Bases: [`MeandraError`](#meandra.core.errors.MeandraError)

Raised when checkpoint operations fail.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **operation** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – The checkpoint operation that failed (e.g., ‘save’, ‘load’, ‘delete’).
  * **checkpoint_id** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – ID of the checkpoint involved, if applicable.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.TimeoutError"></a>

### *exception* meandra.core.errors.TimeoutError(message, timeout_seconds, operation, elapsed_seconds=None, \*\*details)

Bases: [`TimeoutError`](#meandra.core.errors.TimeoutError), [`MeandraError`](#meandra.core.errors.MeandraError)

Raised when an operation exceeds its time limit.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **timeout_seconds** ([*float*](https://docs.python.org/3/library/functions.html#float)) – The timeout that was exceeded.
  * **operation** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Description of the operation that timed out.
  * **elapsed_seconds** (*Optional* *[*[*float*](https://docs.python.org/3/library/functions.html#float) *]*) – Actual elapsed time before timeout, if known.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.ConfigurationError"></a>

### *exception* meandra.core.errors.ConfigurationError(message, config_key=None, \*\*details)

Bases: [`MeandraError`](#meandra.core.errors.MeandraError)

Raised when configuration is invalid or missing.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **config_key** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – The configuration key that caused the error, if applicable.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.RetryExhaustedError"></a>

### *exception* meandra.core.errors.RetryExhaustedError(message, attempts, last_error, \*\*details)

Bases: [`MeandraError`](#meandra.core.errors.MeandraError)

Raised when all retry attempts have been exhausted.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Human-readable error message.
  * **attempts** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Number of attempts made.
  * **last_error** ([*Exception*](https://docs.python.org/3/library/exceptions.html#Exception)) – The last exception that occurred.
  * **\*\*details** (*Any*) – Additional structured error information.

<a id="meandra.core.errors.RetryExhaustedError.to_dict"></a>

#### to_dict()

Convert exception to a dictionary for structured logging.

* **Returns:**
  Structured error representation.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]
