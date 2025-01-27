#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core
============

Defines the core API for constructing and executing data processing pipelines in the Meandra
framework.

The `core` module provides the foundational base classes for pipeline components: nodes and
pipelines. These abstractions establish a standardized interface that users must implement when
specifying custom processing logic.

The design prioritizes:
- Structured, modular, and extensible workflows
- Consistent interaction across processing units
- Seamless integration with framework's execution engine and orchestration mechanisms


Modules
-------
node
    Defines the Node class for building individual nodes in a pipeline.
pipeline
    Defines the Pipeline class for constructing and managing entire pipelines.

Usage
-----
To create a pipeline:

1. Subclass the Node class to implement custom nodes.
2. Use the Pipeline class to assemble and manage these nodes.

See Also
--------
test_core
    Contains tests for the core module.
"""
