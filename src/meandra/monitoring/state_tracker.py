#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.monitoring.state_tracker
================================

"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from meandra.core.node import Node

class StateTracker(ABC):
    """Abstract base class for tracking the execution state of a workflow."""

    @abstractmethod
    def update_state(self, node_id, state):
        """Update the execution state of a node."""
        pass

    @abstractmethod
    def get_state(self, node_id):
        """Retrieve the execution state of a node."""
        pass


    @abstractmethod
    def log_start(self, node: Node) -> None:
        """Log the start of a node execution."""
        pass

    @abstractmethod
    def log_end(self, node: Node, outputs: Dict[str, Any]) -> None:
        """Log the completion of a node execution."""
        pass

# FIXME: Mock implementations for StateTracker and DataManager
class MockStateTracker(StateTracker):
    def __init__(self):
        self.states = {}

    def update_state(self, node_id, state):
        self.states[node_id] = state

    def get_state(self, node_id):
        return self.states.get(node_id, "not_started")
