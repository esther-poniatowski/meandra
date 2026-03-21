"""
meandra.api.fluent
==================

Fluent API for building workflows with method chaining.

This module provides builder classes for creating nodes and workflows
using a fluent, chainable interface.

Examples
--------
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
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from meandra.core.node import Node
from meandra.core.workflow import Workflow


@dataclass
class StepBuilder:
    """
    Fluent builder for creating a Node.

    Attributes
    ----------
    func : Callable
        The function to execute for this node.
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

    Examples
    --------
    >>> builder = step(my_func).in_("x", "y").out("z").depends_on("loader")
    >>> node = builder.build()
    """

    func: Callable[[Dict[str, Any]], Any]
    name: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_checkpointable: bool = False
    accepts_context: bool = False
    input_contract: Optional[Callable[[Dict[str, Any]], None]] = None
    output_contract: Optional[Callable[[Dict[str, Any]], None]] = None

    def named(self, name: str) -> "StepBuilder":
        """Set the node name."""
        self.name = name
        return self

    def in_(self, *keys: str) -> "StepBuilder":
        """Specify input keys."""
        self.inputs = list(keys)
        return self

    def out(self, *keys: str) -> "StepBuilder":
        """Specify output keys."""
        self.outputs = list(keys)
        return self

    def depends_on(self, *names: str) -> "StepBuilder":
        """Specify dependency node names."""
        self.dependencies = list(names)
        return self

    def checkpointable(self, flag: bool = True) -> "StepBuilder":
        """Set whether the node is checkpointable."""
        self.is_checkpointable = flag
        return self

    def context(self, flag: bool = True) -> "StepBuilder":
        """Set whether the node accepts full context."""
        self.accepts_context = flag
        return self

    def with_input_contract(
        self, contract: Callable[[Dict[str, Any]], None]
    ) -> "StepBuilder":
        """Set input validation contract."""
        self.input_contract = contract
        return self

    def with_output_contract(
        self, contract: Callable[[Dict[str, Any]], None]
    ) -> "StepBuilder":
        """Set output validation contract."""
        self.output_contract = contract
        return self

    def build(self) -> Node:
        """
        Build the Node from this builder.

        Returns
        -------
        Node
            Configured Node instance.
        """
        node_name = self.name or self.func.__name__
        return Node(
            name=node_name,
            func=self.func,
            dependencies=self.dependencies,
            inputs=self.inputs,
            outputs=self.outputs,
            is_checkpointable=self.is_checkpointable,
            accepts_context=self.accepts_context,
            input_contract=self.input_contract,
            output_contract=self.output_contract,
        )


@dataclass
class PipelineBuilder:
    """
    Fluent builder for creating a Workflow.

    Attributes
    ----------
    name : str
        Workflow name.
    steps : List[StepBuilder]
        Steps to include in the workflow.

    Examples
    --------
    >>> workflow = (
    ...     pipe("my_workflow")
    ...     .add(step(load).out("data"))
    ...     .add(step(process).in_("data").out("result"))
    ...     .build()
    ... )
    """

    name: str
    steps: List[StepBuilder] = field(default_factory=list)

    def add(self, step: StepBuilder) -> "PipelineBuilder":
        """
        Add a step to the pipeline.

        Parameters
        ----------
        step : StepBuilder
            Step builder to add.

        Returns
        -------
        PipelineBuilder
            Self for chaining.
        """
        self.steps.append(step)
        return self

    def build(self) -> Workflow:
        """
        Build the Workflow from this builder.

        Returns
        -------
        Workflow
            Configured Workflow instance.
        """
        workflow = Workflow(self.name)
        seen_names: set[str] = set()
        for step_builder in self.steps:
            node = step_builder.build()
            if node.name in seen_names:
                raise ValueError(f"Duplicate node name '{node.name}' in workflow '{self.name}'")
            seen_names.add(node.name)
            workflow.add_node(node)
        return workflow


def step(func: Callable[[Dict[str, Any]], Any]) -> StepBuilder:
    """
    Create a StepBuilder from a callable.

    Parameters
    ----------
    func : Callable
        Function to wrap as a node.

    Returns
    -------
    StepBuilder
        Builder for configuring the node.

    Examples
    --------
    >>> node = step(my_function).out("result").build()
    """
    return StepBuilder(func=func)


def pipe(name: str) -> PipelineBuilder:
    """
    Create a PipelineBuilder.

    Parameters
    ----------
    name : str
        Name for the workflow.

    Returns
    -------
    PipelineBuilder
        Builder for configuring the workflow.

    Examples
    --------
    >>> workflow = pipe("my_workflow").add(step(func)).build()
    """
    return PipelineBuilder(name=name)
