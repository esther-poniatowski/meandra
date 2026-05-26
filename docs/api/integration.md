<a id="integration"></a>

# Integration

Adapters connecting Meandra to Tessara (parameter sweeps) and Morpha (typed data structures).

<a id="module-meandra.integration.protocols"></a>

<a id="protocols"></a>

## Protocols

<a id="meandra-integration-protocols"></a>

### meandra.integration.protocols

Stable extension seams for workflow and IO integrations.

<a id="meandra.integration.protocols.NodeTransformer"></a>

### *class* meandra.integration.protocols.NodeTransformer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Transform a node without depending on its concrete field layout.

<a id="meandra.integration.protocols.NodeTransformer.transform_node"></a>

#### transform_node(node)

Transform a single node.

* **Parameters:**
  **node** ([*Node*](core.md#meandra.core.node.Node)) – The node to transform.
* **Returns:**
  The transformed node.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

<a id="meandra.integration.protocols.WorkflowTransformer"></a>

### *class* meandra.integration.protocols.WorkflowTransformer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Transform a workflow through the stable workflow seam.

<a id="meandra.integration.protocols.WorkflowTransformer.transform_workflow"></a>

#### transform_workflow(workflow)

Transform a workflow.

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to transform.
* **Returns:**
  The transformed workflow.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)

<a id="meandra.integration.protocols.IOBackendDescriptor"></a>

### *class* meandra.integration.protocols.IOBackendDescriptor(extension, saver_name, loader_name)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Descriptor for a data backend keyed by file extension.

<a id="meandra.integration.protocols.IOBackendDescriptor.extension"></a>

#### extension *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

File extension this backend handles.

<a id="meandra.integration.protocols.IOBackendDescriptor.saver_name"></a>

#### saver_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the saver class in the backend module.

<a id="meandra.integration.protocols.IOBackendDescriptor.loader_name"></a>

#### loader_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the loader class in the backend module.

<a id="meandra.integration.protocols.IOBackendDescriptor.resolve_saver"></a>

#### resolve_saver(module)

Resolve the saver class from the given module.

* **Parameters:**
  **module** (*Any*) – Module to look up the saver class in.
* **Returns:**
  The saver class, or None if not found.
* **Return type:**
  Optional[Type[Saver]]

<a id="meandra.integration.protocols.IOBackendDescriptor.resolve_loader"></a>

#### resolve_loader(module)

Resolve the loader class from the given module.

* **Parameters:**
  **module** (*Any*) – Module to look up the loader class in.
* **Returns:**
  The loader class, or None if not found.
* **Return type:**
  Optional[Type[Loader]]

<a id="module-meandra.integration.tessara"></a>

<a id="tessara-adapter"></a>

## Tessara Adapter

<a id="meandra-integration-tessara"></a>

### meandra.integration.tessara

Integration adapters for Tessara parameter management.

<a id="meandra.integration.tessara.TessaraNodeAdapter"></a>

### *class* meandra.integration.tessara.TessaraNodeAdapter(params, validate=False)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Adapts Tessara parameters for injection into Meandra nodes.

This adapter bridges the gap between Tessara’s parameter management
and Meandra’s workflow execution by:
- Injecting validated parameters into node functions
- Creating parameter-aware node wrappers
- Supporting both explicit parameter binding and automatic discovery

* **Parameters:**
  * **params** (*ParameterSet*) – Tessara parameter set containing parameters to inject.
  * **validate** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether to validate parameter values before injection.

### Examples

Basic usage with a node function:

```pycon
>>> from tessara import ParameterSet, Param
>>> params = ParameterSet(lr=Param(default=0.01), epochs=Param(default=100))
>>> adapter = TessaraNodeAdapter(params)
>>>
>>> def train(inputs, lr, epochs):
...     return {"model": f"trained with lr={lr}, epochs={epochs}"}
>>>
>>> wrapped = adapter.wrap_function(train)
>>> result = wrapped({"data": [1, 2, 3]})
```

<a id="meandra.integration.tessara.TessaraNodeAdapter.__init__"></a>

#### \_\_init_\_(params, validate=False)

Initialize the adapter with a parameter set.

<a id="meandra.integration.tessara.TessaraNodeAdapter.iter_params"></a>

#### iter_params()

Iterate over parameters with dotted paths.

* **Returns:**
  Tuples of (path, Param-like object).
* **Return type:**
  Iterable[Tuple[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]]

<a id="meandra.integration.tessara.TessaraNodeAdapter.get_param_values"></a>

#### get_param_values(names=None)

Extract parameter values from the parameter set.

* **Parameters:**
  **names** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Specific parameter names to extract. If None, extracts all.
* **Returns:**
  Dictionary mapping parameter names to their current values.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]

<a id="meandra.integration.tessara.TessaraNodeAdapter.wrap_function"></a>

#### wrap_function(func, param_names=None, param_aliases=None, validate=None)

Wrap a function to inject parameters from the parameter set.

* **Parameters:**
  * **func** (*Callable* *[* *...* *,* *Any* *]*) – Function to wrap. Should accept inputs dict plus parameter kwargs.
  * **param_names** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Specific parameters to inject. If None, injects all matching
    function signature parameters.
  * **param_aliases** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Mapping of parameter names to function argument aliases.
  * **validate** (*Optional* *[*[*bool*](https://docs.python.org/3/library/functions.html#bool) *]*) – Whether to validate parameters. Overrides instance setting.
* **Returns:**
  Wrapped function that receives only inputs dict.
* **Return type:**
  Callable[[Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]], Any]

### Examples

```pycon
>>> def process(inputs, threshold=0.5):
...     return {"filtered": [x for x in inputs["data"] if x > threshold]}
>>>
>>> params = ParameterSet(threshold=Param(default=0.7))
>>> adapter = TessaraNodeAdapter(params)
>>> wrapped = adapter.wrap_function(process)
>>> wrapped({"data": [0.3, 0.8, 0.6]})
{'filtered': [0.8]}
```

<a id="meandra.integration.tessara.TessaraNodeAdapter.bind_to_node"></a>

#### bind_to_node(node, param_names=None, param_aliases=None, validate=None)

Create a new node with parameters injected into its function.

* **Parameters:**
  * **node** ([*Node*](core.md#meandra.core.node.Node)) – The node to adapt.
  * **param_names** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Specific parameters to inject. If None, auto-discovers from
    function signature.
  * **param_aliases** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Mapping of parameter names to function argument aliases.
  * **validate** (*Optional* *[*[*bool*](https://docs.python.org/3/library/functions.html#bool) *]*) – Whether to validate parameters. Overrides instance setting.
* **Returns:**
  New node with parameter-injected function.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

<a id="meandra.integration.tessara.TessaraNodeAdapter.adapt_workflow"></a>

#### adapt_workflow(workflow, node_params=None, node_aliases=None, validate=None)

Create a new workflow with parameters injected into specified nodes.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to adapt.
  * **node_params** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]* *]*) – Mapping of node names to parameter names to inject.
    If None, auto-discovers for all nodes.
  * **node_aliases** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]* *]*) – Mapping of node names to parameter alias dicts.
  * **validate** (*Optional* *[*[*bool*](https://docs.python.org/3/library/functions.html#bool) *]*) – Whether to validate parameters. Overrides instance setting.
* **Returns:**
  New workflow with parameter-adapted nodes.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)

<a id="meandra.integration.tessara.TessaraNodeAdapter.transform_node"></a>

#### transform_node(node)

Implement the stable node-transformer seam.

* **Parameters:**
  **node** ([*Node*](core.md#meandra.core.node.Node)) – The node to transform.
* **Returns:**
  Transformed node with injected parameters.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

<a id="meandra.integration.tessara.TessaraNodeAdapter.transform_workflow"></a>

#### transform_workflow(workflow)

Implement the stable workflow-transformer seam.

* **Parameters:**
  **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to transform.
* **Returns:**
  Transformed workflow with injected parameters.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)

<a id="meandra.integration.tessara.SweepOrchestrator"></a>

### *class* meandra.integration.tessara.SweepOrchestrator(orchestrator, sweeper)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Execute a workflow for each parameter combination from a ParamSweeper.

Automates running the same workflow multiple times with different
parameter configurations, collecting results from all runs.

* **Parameters:**
  * **orchestrator** ([*Orchestrator*](orchestration.md#meandra.orchestration.orchestrator.Orchestrator)) – Meandra orchestrator for workflow execution.
  * **sweeper** (*ParamSweeper*) – Tessara parameter sweeper for generating combinations.

### Examples

```pycon
>>> from tessara import ParameterSet, Param, ParamGrid, ParamSweeper
>>> params = ParameterSet(
...     lr=ParamGrid(Param(), sweep_values=[0.01, 0.001]),
...     epochs=Param(default=100),
... )
>>> sweeper = ParamSweeper(params)
>>> sweep_orch = SweepOrchestrator(orchestrator, sweeper)
>>> results = sweep_orch.run_sweep(workflow, inputs)
>>> len(results)  # 2 runs for 2 lr values
2
```

<a id="meandra.integration.tessara.SweepOrchestrator.__init__"></a>

#### \_\_init_\_(orchestrator, sweeper)

Initialize the sweep orchestrator.

<a id="meandra.integration.tessara.SweepOrchestrator.run_sweep"></a>

#### run_sweep(workflow, inputs=None, node_params=None, on_run_complete=None)

Execute the workflow for all parameter combinations.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to execute.
  * **inputs** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]*) – Initial inputs for the workflow.
  * **node_params** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]* *]*) – Mapping of node names to parameter names for injection.
  * **on_run_complete** (*Optional* *[**Callable* *[* *[*[*int*](https://docs.python.org/3/library/functions.html#int) *,* *Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *,* *Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *None* *]* *]*) – Callback called after each run with (index, params_dict, results).
* **Returns:**
  List of results from each parameter combination run.
  Each dict contains:
  - ‘params’: The parameter values used
  - ‘outputs’: The workflow outputs
  - ‘success’: Whether the run completed successfully
  - ‘error’: Error message if failed (only if success=False)
* **Return type:**
  List[Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Any]]

<a id="module-meandra.integration.data"></a>

<a id="data-structure-handlers"></a>

## Data Structure Handlers

<a id="meandra-integration-data"></a>

### meandra.integration.data

Integration adapters for Morpha data structures.

<a id="meandra.integration.data.DataStructureIOHandler"></a>

### *class* meandra.integration.data.DataStructureIOHandler(saver_cls=None, loader_cls=None)

Bases: [`IOHandler`](datastore.md#meandra.datastore.io_handlers.IOHandler)

IOHandler that bridges Meandra’s I/O system with Morpha’s Saver/Loader.

Provides seamless integration between Meandra workflows and Morpha’s
type-safe data persistence layer.

* **Parameters:**
  * **saver_cls** (*Optional* *[**Type* *[**Saver* *]* *]*) – Morpha Saver class for writing. If None, uses auto-detection.
  * **loader_cls** (*Optional* *[**Type* *[**Loader* *]* *]*) – Morpha Loader class for reading. If None, uses auto-detection.

### Examples

```pycon
>>> from morpha.io.savers import SaverPKL
>>> from morpha.io.loaders import LoaderPKL
>>> handler = DataStructureIOHandler(SaverPKL, LoaderPKL)
>>> handler.write("output.pkl", my_data_structure)
>>> data = handler.read("output.pkl")
```

<a id="meandra.integration.data.DataStructureIOHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ['.pkl', '.pickle', '.npy', '.npz', '.yaml', '.yml', '.json', '.h5', '.hdf5']*

File extensions this handler supports.

<a id="meandra.integration.data.DataStructureIOHandler.__init__"></a>

#### \_\_init_\_(saver_cls=None, loader_cls=None)

Initialize with Morpha Saver and Loader classes.

<a id="meandra.integration.data.DataStructureIOHandler.read"></a>

#### read(path)

Read data using Morpha’s Loader.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Loaded data structure.
* **Return type:**
  Any

<a id="meandra.integration.data.DataStructureIOHandler.write"></a>

#### write(path, data)

Write data using Morpha’s Saver.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data structure to write.

<a id="meandra.integration.data.DataStructureIOHandler.register_extension"></a>

#### *classmethod* register_extension(extension, saver_name, loader_name)

Register a custom Saver/Loader by extension.

* **Parameters:**
  * **extension** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – File extension to register (with or without leading dot).
  * **saver_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the Morpha Saver class.
  * **loader_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the Morpha Loader class.

<a id="meandra.integration.data.DataStructureIOHandler.supports"></a>

#### *classmethod* supports(path)

Check if this handler supports the given file path.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  True if the file extension is supported.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.integration.data.create_typed_node"></a>

### meandra.integration.data.create_typed_node(name, func, input_types=None, output_types=None, allow_missing_inputs=False, allow_missing_outputs=False, \*\*kwargs)

Create a Node with type validation contracts.

Creates input and output contracts that validate data types,
supporting both primitive types and Morpha DataStructure types.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Node name.
  * **func** (*Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *Any* *]*) – Node function.
  * **input_types** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Type* *]* *]*) – Mapping of input names to expected types.
  * **output_types** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Type* *]* *]*) – Mapping of output names to expected types.
  * **allow_missing_inputs** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, skip validation for missing input keys.
  * **allow_missing_outputs** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, skip validation for missing output keys.
  * **\*\*kwargs** (*Any*) – Additional arguments passed to Node constructor.
* **Returns:**
  Node with type validation contracts.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

### Examples

```pycon
>>> import numpy as np
>>> def process(inputs):
...     return {"result": inputs["data"] * 2}
>>>
>>> node = create_typed_node(
...     "processor",
...     process,
...     input_types={"data": np.ndarray},
...     output_types={"result": np.ndarray},
... )
```
