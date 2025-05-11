#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core.workflow
=====================

"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from meandra.core.node import Node
from meandra.core.parameters import ParameterSet

class workflow(ABC):
    """
    Abstract base class for a workflow composed of multiple nodes.
    """
    def __init__(self):
        self.nodes = []

    @abstractmethod
    def add_node(self, node, dependencies=None):
        """Add a node to the workflow with optional dependencies."""
        pass


class Workflow:
    def __init__(self, name: str, params: ParameterSet = None):
        self.name = name
        self.nodes = []
        self.params = params or ParameterSet()

    def add_node(self, node: Node):
        """Register a node in the workflow."""
        self.nodes.append(node)

    def execute(self, config: Dict[str, Any]):
        """Apply configuration and execute the workflow."""
        self.params.apply_config(config)  # Set parameter values

        computed_results = {}
        for node in self.nodes:
            # Gather dependencies
            inputs = {dep.name: computed_results[dep.name] for dep in node.dependencies}
            inputs.update({k: v.get_value() for k, v in self.params._params.items()})
            computed_results[node.name] = node.execute(inputs)

        return computed_results
