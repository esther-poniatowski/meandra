<a id="user-facing-api"></a>

# User-Facing API

Fluent and decorator APIs for building workflows with minimal boilerplate.

<a id="module-meandra.api.fluent"></a>

<a id="fluent-api"></a>

## Fluent API

<a id="meandra-api-fluent"></a>

### meandra.api.fluent

Fluent API for building workflows with method chaining.

This module provides builder classes for creating nodes and workflows
using a fluent, chainable interface.

### Notes

The fluent API is an alternative to the decorator-based API for building
workflows programmatically.

### Examples

```pycon
>>> from meandra.api import step, pipe
>>>
>>> def load_data(inputs):
...     return {"data": [1, 2, 3]}
>>>
>>> def process(inputs):
...     return {"result": sum(inputs["data"])}
>>>
>>> workflow = (
...     pipe("my_workflow")
...     .add(step(load_data).out("data"))
...     .add(step(process).in_("data").out("result").depends_on("load_data"))
...     .build()
... )
```

<a id="meandra.api.fluent.StepBuilder"></a>

### *class* meandra.api.fluent.StepBuilder(func, name=None, inputs=<factory>, outputs=<factory>, dependencies=<factory>, is_checkpointable=False, accepts_context=False, input_contract=None, output_contract=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Fluent builder for creating a Node.

### Examples

```pycon
>>> builder = step(my_func).in_("x", "y").out("z").depends_on("loader")
>>> node = builder.build()
```

<a id="meandra.api.fluent.StepBuilder.func"></a>

#### func *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

The function to execute for this node.

<a id="meandra.api.fluent.StepBuilder.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Node name. If None, uses function name.

<a id="meandra.api.fluent.StepBuilder.inputs"></a>

#### inputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Input keys the node expects.

<a id="meandra.api.fluent.StepBuilder.outputs"></a>

#### outputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Output keys the node produces.

<a id="meandra.api.fluent.StepBuilder.dependencies"></a>

#### dependencies *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Names of nodes this node depends on.

<a id="meandra.api.fluent.StepBuilder.is_checkpointable"></a>

#### is_checkpointable *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the node supports checkpointing.

<a id="meandra.api.fluent.StepBuilder.accepts_context"></a>

#### accepts_context *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the node receives full context.

<a id="meandra.api.fluent.StepBuilder.input_contract"></a>

#### input_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="meandra.api.fluent.StepBuilder.output_contract"></a>

#### output_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

<a id="meandra.api.fluent.StepBuilder.named"></a>

#### named(name)

Set the node name.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name to assign to the node.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.in_"></a>

#### in_(\*keys)

Specify input keys.

* **Parameters:**
  **\*keys** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Input key names.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.out"></a>

#### out(\*keys)

Specify output keys.

* **Parameters:**
  **\*keys** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Output key names.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.depends_on"></a>

#### depends_on(\*names)

Specify dependency node names.

* **Parameters:**
  **\*names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Names of upstream nodes this step depends on.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.checkpointable"></a>

#### checkpointable(flag=True)

Set whether the node is checkpointable.

* **Parameters:**
  **flag** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Enable or disable checkpointing.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.context"></a>

#### context(flag=True)

Set whether the node accepts full context.

* **Parameters:**
  **flag** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Enable or disable full context passing.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.with_input_contract"></a>

#### with_input_contract(contract)

Set input validation contract.

* **Parameters:**
  **contract** (*Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *None* *]*) – Callable that validates node inputs.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.with_output_contract"></a>

#### with_output_contract(contract)

Set output validation contract.

* **Parameters:**
  **contract** (*Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *None* *]*) – Callable that validates node outputs.
* **Returns:**
  Self for chaining.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

<a id="meandra.api.fluent.StepBuilder.build"></a>

#### build()

Build the Node from this builder.

* **Returns:**
  Configured Node instance.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

<a id="meandra.api.fluent.StepBuilder.to_spec"></a>

#### to_spec()

Convert the fluent builder into the canonical node specification.

* **Returns:**
  Canonical node specification.
* **Return type:**
  [NodeSpec](#meandra.api.decorators.NodeSpec)

<a id="meandra.api.fluent.PipelineBuilder"></a>

### *class* meandra.api.fluent.PipelineBuilder(name, steps=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Fluent builder for creating a Workflow.

### Examples

```pycon
>>> workflow = (
...     pipe("my_workflow")
...     .add(step(load).out("data"))
...     .add(step(process).in_("data").out("result"))
...     .build()
... )
```

<a id="meandra.api.fluent.PipelineBuilder.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Workflow name.

<a id="meandra.api.fluent.PipelineBuilder.steps"></a>

#### steps *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[StepBuilder](#meandra.api.fluent.StepBuilder)]*

Steps to include in the workflow.

<a id="meandra.api.fluent.PipelineBuilder.add"></a>

#### add(step)

Add a step to the pipeline.

* **Parameters:**
  **step** ([*StepBuilder*](#meandra.api.fluent.StepBuilder)) – Step builder to add.
* **Returns:**
  Self for chaining.
* **Return type:**
  [PipelineBuilder](#meandra.api.fluent.PipelineBuilder)

<a id="meandra.api.fluent.PipelineBuilder.build"></a>

#### build()

Build the Workflow from this builder.

* **Returns:**
  Configured Workflow instance.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)

<a id="meandra.api.fluent.PipelineBuilder.to_spec"></a>

#### to_spec()

Compile the fluent pipeline into the canonical workflow specification.

* **Returns:**
  Canonical workflow specification.
* **Return type:**
  [PipelineSpec](#meandra.api.decorators.PipelineSpec)

<a id="meandra.api.fluent.step"></a>

### meandra.api.fluent.step(func)

Create a StepBuilder from a callable.

* **Parameters:**
  **func** (*Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *Any* *]*) – Function to wrap as a node.
* **Returns:**
  Builder for configuring the node.
* **Return type:**
  [StepBuilder](#meandra.api.fluent.StepBuilder)

### Examples

```pycon
>>> node = step(my_function).out("result").build()
```

<a id="meandra.api.fluent.pipe"></a>

### meandra.api.fluent.pipe(name)

Create a PipelineBuilder.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name for the workflow.
* **Returns:**
  Builder for configuring the workflow.
* **Return type:**
  [PipelineBuilder](#meandra.api.fluent.PipelineBuilder)

### Examples

```pycon
>>> workflow = pipe("my_workflow").add(step(func)).build()
```

<a id="module-meandra.api.decorators"></a>

<a id="decorator-api"></a>

## Decorator API

<a id="meandra-api-decorators"></a>

### meandra.api.decorators

Decorator-based API for declarative workflow definition.

This module provides @node and @pipeline decorators that enable
minimal-boilerplate workflow construction from decorated functions
and classes.

### Examples

Decorating individual functions:

```pycon
>>> @node(outputs=["data"])
... def load_data(inputs):
...     return {"data": [1, 2, 3]}
```

```pycon
>>> @node(inputs=["data"], outputs=["result"], depends_on=["load_data"])
... def process(inputs):
...     return {"result": sum(inputs["data"])}
```

Decorating a class to create a pipeline:

```pycon
>>> @pipeline(name="my_pipeline")
... class MyPipeline:
...     @node(outputs=["data"])
...     def load(self, inputs):
...         return {"data": [1, 2, 3]}
...
...     @node(inputs=["data"], outputs=["result"], depends_on=["load"])
...     def process(self, inputs):
...         return {"result": sum(inputs["data"])}
```

<a id="meandra.api.decorators.NodeSpec"></a>

### *class* meandra.api.decorators.NodeSpec(func, name=None, inputs=<factory>, outputs=<factory>, dependencies=<factory>, is_checkpointable=False, accepts_context=False, input_contract=None, output_contract=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Specification for a node created by the @node decorator.

<a id="meandra.api.decorators.NodeSpec.func"></a>

#### func *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[...], [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

The decorated function.

<a id="meandra.api.decorators.NodeSpec.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Node name. If None, uses function name.

<a id="meandra.api.decorators.NodeSpec.inputs"></a>

#### inputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Input keys the node expects.

<a id="meandra.api.decorators.NodeSpec.outputs"></a>

#### outputs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Output keys the node produces.

<a id="meandra.api.decorators.NodeSpec.dependencies"></a>

#### dependencies *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Names of nodes this node depends on.

<a id="meandra.api.decorators.NodeSpec.is_checkpointable"></a>

#### is_checkpointable *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the node supports checkpointing.

<a id="meandra.api.decorators.NodeSpec.accepts_context"></a>

#### accepts_context *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the node receives full context.

<a id="meandra.api.decorators.NodeSpec.input_contract"></a>

#### input_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Input validation contract.

<a id="meandra.api.decorators.NodeSpec.output_contract"></a>

#### output_contract *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Output validation contract.

<a id="meandra.api.decorators.NodeSpec.to_node"></a>

#### to_node(instance=None)

Convert specification to a Node instance.

* **Parameters:**
  **instance** (*Optional* *[**Any* *]*) – Instance to bind methods to (for class-based pipelines).
* **Returns:**
  Configured Node instance.
* **Return type:**
  [Node](core.md#meandra.core.node.Node)

<a id="meandra.api.decorators.NodeSpec.validate_signature"></a>

#### validate_signature()

Validate that the function signature is compatible with node inputs.

Emits a warning if declared inputs are not in function parameters.

* **Warns:**
  **UserWarning** – If declared inputs are not present in the function signature.

<a id="meandra.api.decorators.node"></a>

### meandra.api.decorators.node(func: F) → F

### meandra.api.decorators.node(\*, name: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None, inputs: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None, outputs: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None, depends_on: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None, checkpointable: [bool](https://docs.python.org/3/library/functions.html#bool) = False, accepts_context: [bool](https://docs.python.org/3/library/functions.html#bool) = False, input_contract: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None) = None, output_contract: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]], [None](https://docs.python.org/3/library/constants.html#None)] | [None](https://docs.python.org/3/library/constants.html#None) = None) → [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[F], F]

Decorator to mark a function as a workflow node.

Can be used with or without arguments:

```pycon
>>> @node
... def my_node(inputs):
...     return {"result": inputs["data"] * 2}
```

```pycon
>>> @node(outputs=["result"], depends_on=["loader"])
... def my_node(inputs):
...     return {"result": inputs["data"] * 2}
```

* **Parameters:**
  * **func** (*Optional* *[**F* *]* *,* *optional*) – The function to decorate (when used without parentheses).
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Node name. Defaults to function name.
  * **inputs** (*List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *,* *optional*) – Input keys the node expects.
  * **outputs** (*List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *,* *optional*) – Output keys the node produces.
  * **depends_on** (*List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *,* *optional*) – Names of nodes this node depends on.
  * **checkpointable** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether the node supports checkpointing. Default False.
  * **accepts_context** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether the node receives full context. Default False.
  * **input_contract** (*Optional* *[**Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *None* *]* *]*) – Input validation function.
  * **output_contract** (*Optional* *[**Callable* *[* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *,* *None* *]* *]*) – Output validation function.
* **Returns:**
  The decorated function with node specification attached.
* **Return type:**
  Union[F, Callable[[F], F]]

<a id="meandra.api.decorators.get_node_spec"></a>

### meandra.api.decorators.get_node_spec(func)

Get the NodeSpec attached to a decorated function.

* **Parameters:**
  **func** (*Callable* *[* *...* *,* *Any* *]*) – Function potentially decorated with @node.
* **Returns:**
  The node specification if decorated, None otherwise.
* **Return type:**
  Optional[[NodeSpec](#meandra.api.decorators.NodeSpec)]

<a id="meandra.api.decorators.is_node"></a>

### meandra.api.decorators.is_node(func)

Check if a function is decorated with @node.

* **Parameters:**
  **func** (*Callable* *[* *...* *,* *Any* *]*) – Function to check.
* **Returns:**
  True if decorated with @node.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.api.decorators.PipelineSpec"></a>

### *class* meandra.api.decorators.PipelineSpec(name, cls, node_specs=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Specification for a pipeline created by the @pipeline decorator.

<a id="meandra.api.decorators.PipelineSpec.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Pipeline name.

<a id="meandra.api.decorators.PipelineSpec.cls"></a>

#### cls *: [Type](https://docs.python.org/3/library/typing.html#typing.Type)[[Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None)*

The decorated class when applicable.

<a id="meandra.api.decorators.PipelineSpec.node_specs"></a>

#### node_specs *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[NodeSpec](#meandra.api.decorators.NodeSpec)]*

Node specifications discovered from decorated methods.

<a id="meandra.api.decorators.PipelineSpec.build"></a>

#### build(instance=None, \*, validate=False, available_inputs=None)

Build a Workflow from the pipeline specification.

* **Parameters:**
  * **instance** (*Optional* *[**Any* *]*) – Instance to bind methods to. If None, creates a new instance.
  * **validate** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to validate the workflow after building. Default False.
  * **available_inputs** (*Optional* *[*[*set*](https://docs.python.org/3/library/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Set of input names available from outside the pipeline.
* **Returns:**
  Configured Workflow instance.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)

<a id="meandra.api.decorators.PipelineSpec.required_inputs"></a>

#### required_inputs()

Return workflow inputs expected from outside the pipeline.

* **Returns:**
  Input names not produced by any node in the pipeline.
* **Return type:**
  [set](https://docs.python.org/3/library/stdtypes.html#set)[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.api.decorators.pipeline"></a>

### meandra.api.decorators.pipeline(cls=None, \*, name=None)

Decorator to mark a class as a workflow pipeline.

Discovers @node decorated methods and assembles them into a workflow.

```pycon
>>> @pipeline(name="my_pipeline")
... class MyPipeline:
...     @node(outputs=["data"])
...     def load(self, inputs):
...         return {"data": [1, 2, 3]}
...
...     @node(inputs=["data"], outputs=["result"], depends_on=["load"])
...     def process(self, inputs):
...         return {"result": sum(inputs["data"])}
```

* **Parameters:**
  * **cls** (*Optional* *[**Type* *[**Any* *]* *]*) – The class to decorate (when used without parentheses).
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Pipeline name. Defaults to class name.
* **Returns:**
  The decorated class with pipeline specification attached.
* **Return type:**
  Union[Type[Any], Callable[[Type[Any]], Type[Any]]]

<a id="meandra.api.decorators.get_pipeline_spec"></a>

### meandra.api.decorators.get_pipeline_spec(cls)

Get the PipelineSpec attached to a decorated class.

* **Parameters:**
  **cls** (*Type* *[**Any* *]*) – Class potentially decorated with @pipeline.
* **Returns:**
  The pipeline specification if decorated, None otherwise.
* **Return type:**
  Optional[[PipelineSpec](#meandra.api.decorators.PipelineSpec)]

<a id="meandra.api.decorators.is_pipeline"></a>

### meandra.api.decorators.is_pipeline(cls)

Check if a class is decorated with @pipeline.

* **Parameters:**
  **cls** (*Type* *[**Any* *]*) – Class to check.
* **Returns:**
  True if decorated with @pipeline.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.api.decorators.build_workflow"></a>

### meandra.api.decorators.build_workflow(pipeline_cls, instance=None, \*, validate=False, available_inputs=None, init_args=None, init_kwargs=None)

Build a Workflow from a @pipeline decorated class.

* **Parameters:**
  * **pipeline_cls** (*Type* *[**Any* *]*) – Class decorated with @pipeline.
  * **instance** (*Optional* *[**Any* *]*) – Instance to use. If None, creates a new instance.
  * **validate** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to validate the workflow after building. Default False.
  * **available_inputs** (*Optional* *[*[*set*](https://docs.python.org/3/library/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Set of input names available from outside the pipeline.
  * **init_args** (*Optional* *[*[*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[**Any* *,*  *...* *]* *]*) – Positional arguments for class instantiation.
  * **init_kwargs** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]*) – Keyword arguments for class instantiation.
* **Returns:**
  Configured Workflow instance.
* **Return type:**
  [Workflow](core.md#meandra.core.workflow.Workflow)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If class is not decorated with @pipeline.
