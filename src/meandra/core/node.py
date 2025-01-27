#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core.node
=================


"""

from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def execute(self, inputs):
        """Execute the node's logic."""
        pass
