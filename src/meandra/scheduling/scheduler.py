"""
meandra.scheduling.scheduler
============================

Workflow scheduling and dependency resolution.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import List, Dict

from meandra.core.workflow import Workflow
from meandra.core.node import Node


class CyclicDependencyError(Exception):
    """Raised when a workflow contains circular dependencies."""

    pass


class Scheduler(ABC):
    """
    Abstract base class for scheduling tasks within a workflow.

    A scheduler determines the execution order of nodes based on their
    dependencies, ensuring that all prerequisites are satisfied before
    a node executes.
    """

    @abstractmethod
    def resolve(self, workflow: Workflow) -> List[List[Node]]:
        """
        Resolve node dependencies and return execution layers.

        Parameters
        ----------
        workflow : Workflow
            The workflow to schedule.

        Returns
        -------
        List[List[Node]]
            Nodes grouped by execution layer. Nodes within the same layer
            can execute in parallel.
        """
        pass


class DAGScheduler(Scheduler):
    """
    Schedule workflow execution using topological sort.

    Uses Kahn's algorithm to resolve dependencies and group nodes into
    execution layers. Nodes within the same layer have no dependencies
    on each other and can execute concurrently.

    Examples
    --------
    >>> scheduler = DAGScheduler()
    >>> layers = scheduler.resolve(workflow)
    >>> for i, layer in enumerate(layers):
    ...     print(f"Layer {i}: {[n.name for n in layer]}")

    Notes
    -----
    The scheduler detects circular dependencies and raises
    CyclicDependencyError if found.
    """

    def resolve(self, workflow: Workflow) -> List[List[Node]]:
        """
        Resolve node dependencies using Kahn's algorithm.

        Parameters
        ----------
        workflow : Workflow
            The workflow to schedule.

        Returns
        -------
        List[List[Node]]
            Execution layers (parallelizable groups).

        Raises
        ------
        CyclicDependencyError
            If the workflow contains circular dependencies.
        KeyError
            If a dependency references a non-existent node.
        """
        if len(workflow) == 0:
            return []

        # Build adjacency list and in-degree count
        # adjacency[a] = nodes that depend on a
        adjacency: Dict[str, List[str]] = {node.name: [] for node in workflow}
        in_degree: Dict[str, int] = {node.name: 0 for node in workflow}

        for node in workflow:
            for dep_name in node.dependencies:
                if dep_name not in workflow:
                    raise KeyError(
                        f"Node '{node.name}' depends on '{dep_name}' which does not exist"
                    )
                adjacency[dep_name].append(node.name)
                in_degree[node.name] += 1

        # Kahn's algorithm with layer grouping
        layers: List[List[Node]] = []
        queue: deque[str] = deque()

        # Initialize queue with nodes that have no dependencies
        for name, degree in in_degree.items():
            if degree == 0:
                queue.append(name)

        processed_count = 0

        while queue:
            # Process all nodes at current depth level (same layer)
            layer_size = len(queue)
            current_layer: List[Node] = []

            for _ in range(layer_size):
                name = queue.popleft()
                current_layer.append(workflow.get_node(name))
                processed_count += 1

                # Decrease in-degree for dependent nodes
                for dependent in adjacency[name]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            layers.append(current_layer)

        # Check for cycles
        if processed_count != len(workflow):
            # Find nodes involved in cycle for error message
            cycle_nodes = [name for name, degree in in_degree.items() if degree > 0]
            raise CyclicDependencyError(
                f"Workflow '{workflow.name}' contains circular dependencies "
                f"involving nodes: {cycle_nodes}"
            )

        return layers

    def get_execution_order(self, workflow: Workflow) -> List[Node]:
        """
        Get a flat execution order (sequential).

        Parameters
        ----------
        workflow : Workflow
            The workflow to schedule.

        Returns
        -------
        List[Node]
            Nodes in valid execution order.
        """
        layers = self.resolve(workflow)
        return [node for layer in layers for node in layer]
