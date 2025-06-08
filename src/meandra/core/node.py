"""
meandra.core.node
=================

"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable

class Node(ABC):
    """Abstract base class for a processing node in the workflow."""

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's logic.

        Arguments
        ---------
        inputs : Dict[str, Any]
            Input data for the node.

        Returns
        -------
        outputs : Dict[str, Any]
            Output data from the node.
        """
        pass

from abc import ABC, abstractmethod


# FIXME: Mock implementation for Node
class MockNode(Node):
    def execute(self, inputs):
        print(f"Executing node with inputs: {inputs}")
        return f"processed_{inputs}"


# --------
class Node:
    """
    Define a processing node in the workflow.

    TODO: Should dependencies be specified at the level of the nodes or the workflow ?
    TODO: Set a default name based on the name of the function.
    TODO: Implement a default approach to pass parameters to the node function automatically, i.e by
    extracting them from a ParameterSet object based on the name of the function arguments. This
    behavior could be overridden at the moment of node definition in order to specify a different
    name to look for in the ParameterSet. This is important in case two nodes call the same function
    but require different parameters, or if two nodes execute different functions which have the
    same argument names.
    TODO: Distinguish between configuration parameters (pre-defined values) and runtime inputs
    (often loaded or passed across nodes, large datasets).
    TODO: Consider creating a separate class to specify the inputs and the outputs.
    TODO: Determine how the inputs and outputs will interact with the data catalog.
    TODO: Add support to define nodes with other callables than standalone functions: for a method
    of a class instance (already instantiated) or a method of a class which is not instantiated yet.
    The latter extension will require to also determine how a class instance will be instantiated
    based on the parameters provided in the workflow configuration.

    Attributes
    ----------
    name : str
        Node name.
    func : Callable[[Dict[str, Any]], Any]
        Function to execute.
    dependencies : List[Node]
        List of dependencies.
    is_checkpointable : bool
        Flag to indicate if the node is checkpointable.
    result : Any
        Computation result.

    Methods
    -------
    execute(inputs: Dict[str, Any]) -> Any
        Execute the node function with the provided inputs.
    """

    def __init__(
        self,
        name: str,
        func: Callable[[Dict[str, Any]], Any],
        dependencies: List["Node"] = None,
        is_checkpointable: bool = False
    ):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.is_checkpointable = is_checkpointable
        self.result = None  # Stores computation result

    def execute(self, inputs: Dict[str, Any]):
        """Execute the node function with the provided inputs."""
        self.result = self.func(inputs)
        return self.result
