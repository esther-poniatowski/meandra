"""
meandra.integration
===================

Integration adapters for connecting Meandra with Tessara and Morpha packages.

This module provides adapters and utilities for:
- Parameter injection from Tessara ParameterSets into workflow nodes
- Automatic parameter sweep execution
- Typed I/O with Morpha DataStructures
"""

from meandra.integration.tessara import TessaraNodeAdapter, SweepOrchestrator
from meandra.integration.data import DataStructureIOHandler

__all__ = [
    "TessaraNodeAdapter",
    "SweepOrchestrator",
    "DataStructureIOHandler",
]
