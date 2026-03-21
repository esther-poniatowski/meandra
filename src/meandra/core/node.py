"""
meandra.core.node
=================

Processing nodes for workflow execution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Optional


@dataclass
class Node:
    """
    Define a processing node in the workflow.

    A node represents a single computation step with explicit inputs,
    outputs, and dependencies on other nodes.

    Attributes
    ----------
    name : str
        Unique identifier for the node within a workflow.
    func : Callable[[Dict[str, Any]], Any]
        Function to execute. Takes a dict of inputs and returns outputs.
    dependencies : List[str]
        Names of nodes this node depends on (outputs needed as inputs).
    inputs : List[str]
        Names of input keys expected from dependencies or workflow inputs.
    outputs : List[str]
        Names of output keys produced by this node.
    is_checkpointable : bool
        Whether node outputs should be checkpointed.
    accepts_context : bool
        If True, the node receives the full context when inputs are not specified.
    input_contract : Optional[Callable[[Dict[str, Any]], None]]
        Optional validator for node inputs.
    output_contract : Optional[Callable[[Dict[str, Any]], None]]
        Optional validator for node outputs.

    Examples
    --------
    >>> def add(inputs):
    ...     return {"sum": inputs["a"] + inputs["b"]}
    >>> node = Node("adder", add, inputs=["a", "b"], outputs=["sum"])
    >>> result = node.execute({"a": 1, "b": 2})
    >>> result
    {'sum': 3}
    """

    name: str
    func: Callable[[Dict[str, Any]], Any]
    dependencies: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    is_checkpointable: bool = False
    accepts_context: bool = False
    input_contract: Optional[Callable[[Dict[str, Any]], None]] = None
    output_contract: Optional[Callable[[Dict[str, Any]], None]] = None

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node function with the provided inputs.

        Parameters
        ----------
        inputs : Dict[str, Any]
            Input data for the node.

        Returns
        -------
        Dict[str, Any]
            Output data from the node.
        """
        if self.input_contract is not None:
            self.input_contract(inputs)
        result = self.func(inputs)
        # Ensure result is a dict
        if not isinstance(result, dict):
            # If function returns a single value, wrap it
            if len(self.outputs) == 1:
                result = {self.outputs[0]: result}
            else:
                raise ValueError(
                    f"Node '{self.name}' must return a dict, got {type(result)}"
                )
        if self.output_contract is not None:
            self.output_contract(result)
        return result

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name
