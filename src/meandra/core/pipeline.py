#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core.pipeline
=====================

"""

from abc import ABC, abstractmethod

class Pipeline(ABC):
    @abstractmethod
    def add_node(self, node, dependencies=None):
        """Add a node to the pipeline with optional dependencies."""
        pass

    @abstractmethod
    def run(self):
        """Execute the pipeline."""
        pass
