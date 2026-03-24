"""
meandra.core.graph
==================

Graph algorithms shared across the framework.

Functions
---------
topological_layers
    Compute a layered topological ordering using Kahn's algorithm.
"""

from collections import deque
from typing import Dict, List, Mapping, Sequence, TypeVar

T = TypeVar("T")


def topological_layers(
    nodes: Mapping[str, T],
    dependencies: Mapping[str, Sequence[str]],
) -> List[List[T]]:
    """
    Compute a layered topological ordering using Kahn's algorithm.

    Nodes within the same layer have no mutual dependencies and can be
    processed concurrently.

    Parameters
    ----------
    nodes : Mapping[str, T]
        Mapping of node name to node object.
    dependencies : Mapping[str, Sequence[str]]
        Mapping of node name to the names it depends on.
        Every dependency name must exist as a key in *nodes*.

    Returns
    -------
    List[List[T]]
        Nodes grouped into execution layers.  The first layer contains
        nodes with no dependencies; subsequent layers contain nodes
        whose dependencies all appear in earlier layers.

    Raises
    ------
    KeyError
        If a dependency references a name not present in *nodes*.

    Notes
    -----
    If the graph contains a cycle, the returned layers will be
    incomplete (fewer total items than ``len(nodes)``).  Callers are
    responsible for detecting this condition and raising an appropriate
    error.
    """
    # Build adjacency list and in-degree count
    adjacency: Dict[str, List[str]] = {name: [] for name in nodes}
    in_degree: Dict[str, int] = {name: 0 for name in nodes}

    for name in nodes:
        for dep_name in dependencies.get(name, []):
            if dep_name not in nodes:
                raise KeyError(
                    f"Node '{name}' depends on '{dep_name}' which does not exist"
                )
            adjacency[dep_name].append(name)
            in_degree[name] += 1

    # Seed the queue with zero-degree nodes
    queue: deque[str] = deque(
        name for name, degree in in_degree.items() if degree == 0
    )

    layers: List[List[T]] = []

    while queue:
        layer_size = len(queue)
        current_layer: List[T] = []

        for _ in range(layer_size):
            name = queue.popleft()
            current_layer.append(nodes[name])

            for dependent in adjacency[name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        layers.append(current_layer)

    return layers
