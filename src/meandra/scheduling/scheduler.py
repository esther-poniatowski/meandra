"""
meandra.scheduling.scheduler
============================

Workflow scheduling and dependency resolution.

Classes
-------
Scheduler
    Abstract base class for scheduling tasks within a workflow.
DAGScheduler
    Schedule workflow execution using topological sort.
"""

from abc import ABC, abstractmethod
from typing import List

from meandra.core.workflow import Workflow
from meandra.core.node import Node
from meandra.core.errors import DependencyResolutionError
from meandra.core.graph import topological_layers


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

    Notes
    -----
    The scheduler detects circular dependencies and raises
    DependencyResolutionError if found.

    Examples
    --------
    >>> scheduler = DAGScheduler()
    >>> layers = scheduler.resolve(workflow)
    >>> for i, layer in enumerate(layers):
    ...     print(f"Layer {i}: {[n.name for n in layer]}")
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
        DependencyResolutionError
            If the workflow contains circular dependencies.
        KeyError
            If a dependency references a non-existent node.
        """
        if len(workflow) == 0:
            return []

        nodes = {node.name: node for node in workflow}
        deps = {node.name: node.dependencies for node in workflow}

        layers = topological_layers(nodes, deps)

        # Check for cycles
        processed_count = sum(len(layer) for layer in layers)
        if processed_count != len(workflow):
            processed_names = {n.name for layer in layers for n in layer}
            cycle_nodes = [name for name in nodes if name not in processed_names]
            raise DependencyResolutionError(
                f"Workflow '{workflow.name}' contains circular dependencies "
                f"involving nodes: {cycle_nodes}",
                workflow_name=workflow.name,
                cycle=cycle_nodes,
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
