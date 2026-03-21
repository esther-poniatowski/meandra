"""
meandra.cli
===========

Provides a command-line interface for launching and managing workflows with configurable runtime
parameters.

The `cli` module implements the command-line entry points and sub-commands which serve as the
primary interface for dynamic instantiation and configuration of workflows.
"""

from meandra.cli_app import app

__all__ = ["app"]
