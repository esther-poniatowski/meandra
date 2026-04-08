"""
meandra.api.decorators
======================

Decorator-based API for declarative workflow definition.

This module provides `@node` and `@pipeline` decorators that enable
minimal-boilerplate workflow construction from decorated functions
and classes.

Examples
--------
Decorating individual functions:

>>> @node(outputs=["data"])
... def load_data(inputs):
...     return {"data": [1, 2, 3]}

>>> @node(inputs=["data"], outputs=["result"], depends_on=["load_data"])
... def process(inputs):
...     return {"result": sum(inputs["data"])}

Decorating a class to create a pipeline:

>>> @pipeline(name="my_pipeline")
... class MyPipeline:
...     @node(outputs=["data"])
...     def load(self, inputs):
...         return {"data": [1, 2, 3]}
...
...     @node(inputs=["data"], outputs=["result"], depends_on=["load"])
...     def process(self, inputs):
...         return {"result": sum(inputs["data"])}

Classes
-------
NodeSpec
    Specification for a node created by the @node decorator.
PipelineSpec
    Specification for a pipeline created by the @pipeline decorator.

Functions
---------
node
    Decorator to mark a function as a workflow node.
get_node_spec
    Get the NodeSpec attached to a decorated function.
is_node
    Check if a function is decorated with @node.
pipeline
    Decorator to mark a class as a workflow pipeline.
get_pipeline_spec
    Get the PipelineSpec attached to a decorated class.
is_pipeline
    Check if a class is decorated with @pipeline.
build_workflow
    Build a Workflow from a @pipeline decorated class.
"""

from dataclasses import dataclass, field
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)
import inspect
import warnings

from meandra.core.node import Node
from meandra.core.workflow import Workflow
from meandra.core.errors import ValidationError as WorkflowValidationError


# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class NodeSpec:
    """
    Specification for a node created by the @node decorator.

    Attributes
    ----------
    func : Callable
        The decorated function.
    name : Optional[str]
        Node name. If None, uses function name.
    inputs : List[str]
        Input keys the node expects.
    outputs : List[str]
        Output keys the node produces.
    dependencies : List[str]
        Names of nodes this node depends on.
    is_checkpointable : bool
        Whether the node supports checkpointing.
    accepts_context : bool
        Whether the node receives full context.
    input_contract : Optional[Callable]
        Input validation contract.
    output_contract : Optional[Callable]
        Output validation contract.
    """

    func: Callable[..., Any]
    name: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_checkpointable: bool = False
    accepts_context: bool = False
    input_contract: Optional[Callable[[Dict[str, Any]], None]] = None
    output_contract: Optional[Callable[[Dict[str, Any]], None]] = None

    def to_node(self, instance: Optional[Any] = None) -> Node:
        """
        Convert specification to a Node instance.

        Parameters
        ----------
        instance : Optional[Any]
            Instance to bind methods to (for class-based pipelines).

        Returns
        -------
        Node
            Configured Node instance.
        """
        node_name = self.name or self.func.__name__

        if instance is not None:
            # Bind method to instance
            func = lambda inputs, inst=instance, fn=self.func: fn(inst, inputs)
        else:
            func = self.func

        return Node(
            name=node_name,
            func=func,
            dependencies=list(self.dependencies),
            inputs=list(self.inputs),
            outputs=list(self.outputs),
            is_checkpointable=self.is_checkpointable,
            accepts_context=self.accepts_context,
            input_contract=self.input_contract,
            output_contract=self.output_contract,
        )

    def validate_signature(self) -> None:
        """
        Validate that the function signature is compatible with node inputs.

        Emits a warning if declared inputs are not in function parameters.

        Warns
        -----
        UserWarning
            If declared inputs are not present in the function signature.
        """
        sig = inspect.signature(self.func)
        params = set(sig.parameters.keys())
        if "inputs" in params:
            return
        missing = [name for name in self.inputs if name not in params]
        if missing:
            warnings.warn(
                f"Node '{self.name or self.func.__name__}' declared inputs {missing} "
                "but they are not present in the function signature.",
                UserWarning,
            )


# Marker attribute for decorated functions
_NODE_SPEC_ATTR = "_meandra_node_spec"


@overload
def node(func: F) -> F: ...


@overload
def node(
    *,
    name: Optional[str] = None,
    inputs: Optional[List[str]] = None,
    outputs: Optional[List[str]] = None,
    depends_on: Optional[List[str]] = None,
    checkpointable: bool = False,
    accepts_context: bool = False,
    input_contract: Optional[Callable[[Dict[str, Any]], None]] = None,
    output_contract: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Callable[[F], F]: ...


def node(
    func: Optional[F] = None,
    *,
    name: Optional[str] = None,
    inputs: Optional[List[str]] = None,
    outputs: Optional[List[str]] = None,
    depends_on: Optional[List[str]] = None,
    checkpointable: bool = False,
    accepts_context: bool = False,
    input_contract: Optional[Callable[[Dict[str, Any]], None]] = None,
    output_contract: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to mark a function as a workflow node.

    Can be used with or without arguments:

    >>> @node
    ... def my_node(inputs):
    ...     return {"result": inputs["data"] * 2}

    >>> @node(outputs=["result"], depends_on=["loader"])
    ... def my_node(inputs):
    ...     return {"result": inputs["data"] * 2}

    Parameters
    ----------
    func : Optional[F], optional
        The function to decorate (when used without parentheses).
    name : str, optional
        Node name. Defaults to function name.
    inputs : List[str], optional
        Input keys the node expects.
    outputs : List[str], optional
        Output keys the node produces.
    depends_on : List[str], optional
        Names of nodes this node depends on.
    checkpointable : bool
        Whether the node supports checkpointing. Default False.
    accepts_context : bool
        Whether the node receives full context. Default False.
    input_contract : Optional[Callable[[Dict[str, Any]], None]]
        Input validation function.
    output_contract : Optional[Callable[[Dict[str, Any]], None]]
        Output validation function.

    Returns
    -------
    Union[F, Callable[[F], F]]
        The decorated function with node specification attached.
    """

    def decorator(fn: F) -> F:
        spec = NodeSpec(
            func=fn,
            name=name,
            inputs=inputs or [],
            outputs=outputs or [],
            dependencies=depends_on or [],
            is_checkpointable=checkpointable,
            accepts_context=accepts_context,
            input_contract=input_contract,
            output_contract=output_contract,
        )

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        setattr(wrapper, _NODE_SPEC_ATTR, spec)
        return wrapper  # type: ignore[return-value]

    if func is not None:
        # Used without parentheses: @node
        return decorator(func)

    # Used with parentheses: @node(...)
    return decorator


def get_node_spec(func: Callable[..., Any]) -> Optional[NodeSpec]:
    """
    Get the NodeSpec attached to a decorated function.

    Parameters
    ----------
    func : Callable[..., Any]
        Function potentially decorated with @node.

    Returns
    -------
    Optional[NodeSpec]
        The node specification if decorated, None otherwise.
    """
    return getattr(func, _NODE_SPEC_ATTR, None)


def is_node(func: Callable[..., Any]) -> bool:
    """
    Check if a function is decorated with @node.

    Parameters
    ----------
    func : Callable[..., Any]
        Function to check.

    Returns
    -------
    bool
        True if decorated with @node.
    """
    return hasattr(func, _NODE_SPEC_ATTR)


@dataclass
class PipelineSpec:
    """
    Specification for a pipeline created by the @pipeline decorator.

    Attributes
    ----------
    name : str
        Pipeline name.
    cls : Optional[Type]
        The decorated class when applicable.
    node_specs : List[NodeSpec]
        Node specifications discovered from decorated methods.
    """

    name: str
    cls: Optional[Type[Any]]
    node_specs: List[NodeSpec] = field(default_factory=list)

    def build(
        self,
        instance: Optional[Any] = None,
        *,
        validate: bool = False,
        available_inputs: Optional[set[str]] = None,
    ) -> Workflow:
        """
        Build a Workflow from the pipeline specification.

        Parameters
        ----------
        instance : Optional[Any]
            Instance to bind methods to. If None, creates a new instance.
        validate : bool
            Whether to validate the workflow after building. Default False.
        available_inputs : Optional[set[str]]
            Set of input names available from outside the pipeline.

        Returns
        -------
        Workflow
            Configured Workflow instance.
        """
        if instance is None and self.cls is not None:
            instance = self.cls()

        workflow = Workflow(name=self.name)
        seen_names: set[str] = set()

        for spec in self.node_specs:
            spec.validate_signature()
            node = spec.to_node(instance)
            if node.name in seen_names:
                raise ValueError(f"Duplicate node name '{node.name}' in pipeline '{self.name}'")
            seen_names.add(node.name)
            workflow.add_node(node)

        if validate:
            result = workflow.validate(available_inputs=available_inputs)
            if not result.valid:
                raise WorkflowValidationError(
                    "Workflow validation failed",
                    workflow_name=workflow.name,
                    errors=result.errors,
                    warnings=result.warnings,
                )

        return workflow

    def required_inputs(self) -> set[str]:
        """
        Return workflow inputs expected from outside the pipeline.

        Returns
        -------
        set[str]
            Input names not produced by any node in the pipeline.
        """
        produced: set[str] = set()
        required: set[str] = set()
        for spec in self.node_specs:
            for input_name in spec.inputs:
                if input_name not in produced:
                    required.add(input_name)
            produced.update(spec.outputs)
        return required


# Marker attribute for decorated classes
_PIPELINE_SPEC_ATTR = "_meandra_pipeline_spec"


def pipeline(
    cls: Optional[Type[Any]] = None,
    *,
    name: Optional[str] = None,
) -> Union[Type[Any], Callable[[Type[Any]], Type[Any]]]:
    """
    Decorator to mark a class as a workflow pipeline.

    Discovers @node decorated methods and assembles them into a workflow.

    >>> @pipeline(name="my_pipeline")
    ... class MyPipeline:
    ...     @node(outputs=["data"])
    ...     def load(self, inputs):
    ...         return {"data": [1, 2, 3]}
    ...
    ...     @node(inputs=["data"], outputs=["result"], depends_on=["load"])
    ...     def process(self, inputs):
    ...         return {"result": sum(inputs["data"])}

    Parameters
    ----------
    cls : Optional[Type[Any]]
        The class to decorate (when used without parentheses).
    name : str, optional
        Pipeline name. Defaults to class name.

    Returns
    -------
    Union[Type[Any], Callable[[Type[Any]], Type[Any]]]
        The decorated class with pipeline specification attached.
    """

    def decorator(klass: Type[Any]) -> Type[Any]:
        pipeline_name = name or klass.__name__

        # Discover @node decorated methods
        node_specs: List[NodeSpec] = []
        for attr_name, attr in klass.__dict__.items():
            if attr_name.startswith("_"):
                continue
            if callable(attr):
                spec = get_node_spec(attr)
                if spec is not None:
                    # Update spec name if not explicitly set
                    if spec.name is None:
                        spec.name = attr_name
                    node_specs.append(spec)

        # Detect duplicate node names
        names = [spec.name or spec.func.__name__ for spec in node_specs]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            dup_list = ", ".join(sorted(duplicates))
            raise ValueError(f"Duplicate node names in pipeline '{pipeline_name}': {dup_list}")

        # Stable ordering by definition order in class __dict__
        spec = PipelineSpec(
            name=pipeline_name,
            cls=klass,
            node_specs=node_specs,
        )

        setattr(klass, _PIPELINE_SPEC_ATTR, spec)
        return klass

    if cls is not None:
        # Used without parentheses: @pipeline
        return decorator(cls)

    # Used with parentheses: @pipeline(...)
    return decorator


def get_pipeline_spec(cls: Type[Any]) -> Optional[PipelineSpec]:
    """
    Get the PipelineSpec attached to a decorated class.

    Parameters
    ----------
    cls : Type[Any]
        Class potentially decorated with @pipeline.

    Returns
    -------
    Optional[PipelineSpec]
        The pipeline specification if decorated, None otherwise.
    """
    return getattr(cls, _PIPELINE_SPEC_ATTR, None)


def is_pipeline(cls: Type[Any]) -> bool:
    """
    Check if a class is decorated with @pipeline.

    Parameters
    ----------
    cls : Type[Any]
        Class to check.

    Returns
    -------
    bool
        True if decorated with @pipeline.
    """
    return hasattr(cls, _PIPELINE_SPEC_ATTR)


def build_workflow(
    pipeline_cls: Type[Any],
    instance: Optional[Any] = None,
    *,
    validate: bool = False,
    available_inputs: Optional[set[str]] = None,
    init_args: Optional[tuple[Any, ...]] = None,
    init_kwargs: Optional[Dict[str, Any]] = None,
) -> Workflow:
    """
    Build a Workflow from a @pipeline decorated class.

    Parameters
    ----------
    pipeline_cls : Type[Any]
        Class decorated with @pipeline.
    instance : Optional[Any]
        Instance to use. If None, creates a new instance.
    validate : bool
        Whether to validate the workflow after building. Default False.
    available_inputs : Optional[set[str]]
        Set of input names available from outside the pipeline.
    init_args : Optional[tuple[Any, ...]]
        Positional arguments for class instantiation.
    init_kwargs : Optional[Dict[str, Any]]
        Keyword arguments for class instantiation.

    Returns
    -------
    Workflow
        Configured Workflow instance.

    Raises
    ------
    ValueError
        If class is not decorated with @pipeline.
    """
    spec = get_pipeline_spec(pipeline_cls)
    if spec is None:
        raise ValueError(f"{pipeline_cls.__name__} is not decorated with @pipeline")
    if instance is None:
        init_args = init_args or ()
        init_kwargs = init_kwargs or {}
        instance = pipeline_cls(*init_args, **init_kwargs)
    return spec.build(instance, validate=validate, available_inputs=available_inputs)
