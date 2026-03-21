"""
meandra.api
===========

Backward-compatible re-export of API components.

This module re-exports all public API components from the meandra.api package.
New code should import directly from meandra.api.

Examples
--------
>>> # Both import styles work:
>>> from meandra.api import step, pipe, node, pipeline
>>> from meandra import api
>>> workflow = api.pipe("my_workflow").add(api.step(func)).build()
"""

# Re-export fluent API
from meandra.api.fluent import (
    StepBuilder,
    PipelineBuilder,
    step,
    pipe,
)

# Re-export decorator API
from meandra.api.decorators import (
    NodeSpec,
    PipelineSpec,
    node,
    pipeline,
    build_workflow,
)

__all__ = [
    # Fluent API
    "StepBuilder",
    "PipelineBuilder",
    "step",
    "pipe",
    # Decorator API
    "NodeSpec",
    "PipelineSpec",
    "node",
    "pipeline",
    "build_workflow",
]
