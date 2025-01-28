#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core.workflow
=====================

"""

from abc import ABC, abstractmethod
from typing import Any, Dict

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


# FIXME: Mock implementation for workflow
class Mockworkflow(workflow):
    def __init__(self):
        self.nodes = []

    def add_node(self, node, dependencies=None):
        self.nodes.append(node)
