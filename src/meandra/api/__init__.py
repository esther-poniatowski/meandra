"""
meandra.api
===========

User-facing API for building workflows with minimal boilerplate.

This module provides two approaches for workflow definition:

1. **Fluent API**: Chain methods to build nodes and workflows.
2. **Decorator API**: Use @node and @pipeline decorators.

Fluent API Example
------------------
>>> from meandra.api import step, pipe
>>> workflow = (
...     pipe("my_workflow")
...     .add(step(load_data).out("data"))
...     .add(step(process).in_("data").out("result").depends_on("load_data"))
...     .build()
... )

Decorator API Example
---------------------
>>> from meandra.api import pipeline, node, build_workflow
>>> @pipeline(name="my_workflow")
... class MyPipeline:
...     @node(outputs=["data"])
...     def load_data(self, inputs):
...         return {"data": [1, 2, 3]}
...
...     @node(inputs=["data"], outputs=["result"], depends_on=["load_data"])
...     def process(self, inputs):
...         return {"result": sum(inputs["data"])}
>>>
>>> workflow = build_workflow(MyPipeline)
"""

# Fluent API
from meandra.api.fluent import (
    StepBuilder,
    PipelineBuilder,
    step,
    pipe,
)

# Decorator API
from meandra.api.decorators import (
    node,
    pipeline,
    NodeSpec,
    PipelineSpec,
    get_node_spec,
    get_pipeline_spec,
    is_node,
    is_pipeline,
    build_workflow,
)

__all__ = [
    # Fluent API
    "StepBuilder",
    "PipelineBuilder",
    "step",
    "pipe",
    # Decorator API
    "node",
    "pipeline",
    "NodeSpec",
    "PipelineSpec",
    "get_node_spec",
    "get_pipeline_spec",
    "is_node",
    "is_pipeline",
    "build_workflow",
]
