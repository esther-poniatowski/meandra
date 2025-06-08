"""
meandra.core
============

Defines the core API for constructing and executing data processing workflows in the Meandra
framework.

The `core` module provides the foundational base classes for workflow components: nodes and
workflows. These abstractions establish a standardized interface that users must implement when
specifying custom processing logic.

The design prioritizes:
- Structured, modular, and extensible workflows
- Consistent interaction across processing units
- Seamless integration with framework's execution engine and orchestration mechanisms


Modules
-------
node
    Defines the Node class for building individual nodes in a workflow.
workflow
    Defines the Workflow class for constructing and managing entire workflows.

Usage
-----
To create a workflow:

1. Subclass the Node class to implement custom nodes.
2. Use the workflow class to assemble and manage these nodes.

See Also
--------
test_core
    Contains tests for the core module.
"""
