"""
meandra.core.workflow
=====================

Workflow definition and management.
"""

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Dict, List, Iterator, Set, Tuple, Optional

from meandra.core.node import Node
from meandra.configuration.mod import ConfigProvider


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails."""

    def __init__(self, message: str, errors: List[str]):
        super().__init__(message)
        self.errors = errors


@dataclass
class ValidationResult:
    """Result of workflow validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        """Raise WorkflowValidationError if validation failed."""
        if not self.valid:
            raise WorkflowValidationError(
                f"Workflow validation failed with {len(self.errors)} error(s)",
                errors=self.errors,
            )


@dataclass
class Workflow:
    """
    Define a workflow composed of multiple processing nodes.

    A workflow is a directed acyclic graph (DAG) of nodes, where each node
    represents a computation step with explicit dependencies.

    Attributes
    ----------
    name : str
        Unique identifier for the workflow.
    nodes : Dict[str, Node]
        Mapping of node names to Node instances.

    Examples
    --------
    >>> def load_data(inputs):
    ...     return {"data": [1, 2, 3]}
    >>> def process(inputs):
    ...     return {"result": sum(inputs["data"])}
    >>> wf = Workflow("example")
    >>> wf.add_node(Node("loader", load_data, outputs=["data"]))
    >>> wf.add_node(Node("processor", process, dependencies=["loader"], inputs=["data"], outputs=["result"]))
    """

    name: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    _validation_cache: Dict[Tuple[str, Optional[Tuple[str, ...]]], ValidationResult] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def add_node(self, node: Node) -> None:
        """
        Register a node in the workflow.

        Parameters
        ----------
        node : Node
            Node to add to the workflow.

        Raises
        ------
        ValueError
            If a node with the same name already exists.
        """
        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists in workflow '{self.name}'")
        self.nodes[node.name] = node
        self._validation_cache.clear()

    def get_node(self, name: str) -> Node:
        """
        Get a node by name.

        Parameters
        ----------
        name : str
            Name of the node.

        Returns
        -------
        Node
            The requested node.

        Raises
        ------
        KeyError
            If node does not exist.
        """
        if name not in self.nodes:
            raise KeyError(f"Node '{name}' not found in workflow '{self.name}'")
        return self.nodes[name]

    def __iter__(self) -> Iterator[Node]:
        """Iterate over nodes in the workflow."""
        return iter(self.nodes.values())

    def __len__(self) -> int:
        """Return number of nodes in the workflow."""
        return len(self.nodes)

    def __contains__(self, name: str) -> bool:
        """Check if a node exists by name."""
        return name in self.nodes

    def validate(
        self, available_inputs: Optional[Set[str] | ConfigProvider] = None
    ) -> ValidationResult:
        """
        Validate the workflow structure.

        Checks for:
        - Missing dependencies (nodes that reference non-existent nodes)
        - Cyclic dependencies
        - Unsatisfiable inputs (inputs not provided by dependencies or available_inputs)

        Parameters
        ----------
        available_inputs : Optional[Set[str] | ConfigProvider]
            Set of input keys that will be provided at execution time, or a
            ConfigProvider to resolve and infer available keys.
            If None, input satisfiability is not checked.

        Returns
        -------
        ValidationResult
            Validation result with errors and warnings.

        Examples
        --------
        >>> wf = Workflow("test")
        >>> wf.add_node(Node("a", func, outputs=["x"]))
        >>> wf.add_node(Node("b", func, dependencies=["a"], inputs=["x"]))
        >>> result = wf.validate()
        >>> result.valid
        True
        """
        available_inputs_set = self._resolve_available_inputs(available_inputs)
        inputs_key = None if available_inputs_set is None else tuple(sorted(available_inputs_set))
        cache_key = (self.structure_hash(), inputs_key)
        cached = self._validation_cache.get(cache_key)
        if cached is not None:
            return cached

        errors: List[str] = []
        warnings: List[str] = []

        # Check 1: Missing dependencies
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(
                        f"Node '{node.name}' depends on '{dep}' which does not exist"
                    )

        # Check 2: Cyclic dependencies (Kahn's algorithm)
        topological_order: List[Node] = []
        if not errors:
            topological_order = self._topological_order()
            if len(topological_order) != len(self.nodes):
                cycle_nodes = [
                    name for name in self.nodes if name not in {n.name for n in topological_order}
                ]
                errors.append(
                    f"Cyclic dependency detected involving nodes: {cycle_nodes}"
                )

        # Check 3: Input satisfiability
        if available_inputs_set is not None and not errors:
            for node in topological_order:
                allowed_inputs = self._allowed_inputs_for_node(node, available_inputs_set)
                for input_key in node.inputs:
                    if input_key not in allowed_inputs:
                        errors.append(
                            f"Node '{node.name}' requires input '{input_key}' "
                            f"which is not provided by dependencies or workflow inputs"
                        )

        # Warnings: nodes with no outputs but with dependents
        dependents = self._dependents_map()
        for node in self.nodes.values():
            if not node.outputs and dependents.get(node.name):
                warnings.append(
                    f"Node '{node.name}' has no outputs; "
                    f"its results won't be available to other nodes"
                )
        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
        self._validation_cache[cache_key] = result
        return result

    def structure_hash(self) -> str:
        """
        Compute a stable hash of the workflow structure.

        Includes node names, dependencies, inputs, outputs, and flags.
        """
        payload = {
            "name": self.name,
            "nodes": [
                {
                    "name": node.name,
                    "dependencies": sorted(node.dependencies),
                    "inputs": sorted(node.inputs),
                    "outputs": sorted(node.outputs),
                    "accepts_context": node.accepts_context,
                    "is_checkpointable": node.is_checkpointable,
                }
                for node in sorted(self.nodes.values(), key=lambda n: n.name)
            ],
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return sha256(encoded).hexdigest()

    def _topological_order(self) -> List[Node]:
        """Return nodes in topological order using Kahn's algorithm."""
        in_degree: Dict[str, int] = {name: 0 for name in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node.name] += 1

        queue: deque[str] = deque()
        for name, degree in in_degree.items():
            if degree == 0:
                queue.append(name)

        order: List[Node] = []
        while queue:
            current = queue.popleft()
            order.append(self.nodes[current])
            for node in self.nodes.values():
                if current in node.dependencies:
                    in_degree[node.name] -= 1
                    if in_degree[node.name] == 0:
                        queue.append(node.name)

        return order

    def _allowed_inputs_for_node(self, node: Node, available_inputs: Set[str]) -> Set[str]:
        """Compute the allowed inputs for a node based on dependencies."""
        allowed = set(available_inputs)
        for dep_name in node.dependencies:
            dep = self.nodes.get(dep_name)
            if dep is not None:
                allowed.update(dep.outputs)
        return allowed

    def _dependents_map(self) -> Dict[str, List[str]]:
        """Build a map of node name to its dependents."""
        dependents: Dict[str, List[str]] = {name: [] for name in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in dependents:
                    dependents[dep].append(node.name)
        return dependents

    def _resolve_available_inputs(
        self, available_inputs: Optional[Set[str] | ConfigProvider]
    ) -> Optional[Set[str]]:
        """Resolve available inputs from a set or ConfigProvider."""
        if available_inputs is None:
            return None
        if isinstance(available_inputs, ConfigProvider):
            available_inputs.resolve()
            return set(available_inputs.to_dict().keys())
        return set(available_inputs)

    def build_model(self) -> "WorkflowModel":
        """
        Build a canonical workflow model for execution and inspection.

        Returns
        -------
        WorkflowModel
            Canonical representation of nodes, edges, and IO keys.
        """
        edges: List[Tuple[str, str]] = []
        inputs: Set[str] = set()
        outputs: Set[str] = set()

        for node in self.nodes.values():
            for dep in node.dependencies:
                edges.append((dep, node.name))
            outputs.update(node.outputs)
            inputs.update(node.inputs)

        return WorkflowModel(
            name=self.name,
            nodes=list(self.nodes.values()),
            edges=edges,
            inputs=sorted(inputs),
            outputs=sorted(outputs),
        )


@dataclass(frozen=True)
class WorkflowModel:
    """
    Canonical workflow representation.

    Attributes
    ----------
    name : str
        Workflow name.
    nodes : List[Node]
        Nodes in the workflow.
    edges : List[Tuple[str, str]]
        Directed edges as (dependency, dependent).
    inputs : List[str]
        Unique input keys expected by nodes.
    outputs : List[str]
        Unique output keys produced by nodes.
    """

    name: str
    nodes: List[Node]
    edges: List[Tuple[str, str]]
    inputs: List[str]
    outputs: List[str]
