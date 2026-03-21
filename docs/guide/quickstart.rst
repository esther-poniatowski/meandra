Quickstart Guide
================

Installation
------------

Install Meandra using pip::

    pip install meandra

For development installation::

    git clone https://github.com/esther-poniatowski/meandra.git
    cd meandra
    pip install -e ".[dev]"


Your First Pipeline
-------------------

1. **Define nodes** using the ``@node`` decorator::

    from meandra.api import node

    @node(outputs=["data"])
    def load_data(inputs):
        return {"data": [1, 2, 3, 4, 5]}

    @node(inputs=["data"], outputs=["total"], depends_on=["load_data"])
    def sum_data(inputs):
        return {"total": sum(inputs["data"])}

2. **Create a pipeline** class::

    from meandra.api import pipeline

    @pipeline(name="my_pipeline")
    class MyPipeline:
        @node(outputs=["data"])
        def load(self, inputs):
            return {"data": [1, 2, 3, 4, 5]}

        @node(inputs=["data"], outputs=["total"], depends_on=["load"])
        def process(self, inputs):
            return {"total": sum(inputs["data"])}

3. **Build and run** the workflow::

    from meandra.api import build_workflow
    from meandra.orchestration import SchedulingOrchestrator

    workflow = build_workflow(MyPipeline, validate=True, available_inputs=set())
    orchestrator = SchedulingOrchestrator()
    result = orchestrator.run(workflow, {})
    print(result["total"])  # 15


Using the CLI
-------------

Run a pipeline from the command line::

    meandra run mymodule:MyPipeline --config config.yaml
    # The CLI validates the pipeline before execution.

Validate a configuration::

    meandra validate config.yaml --pipeline mymodule:MyPipeline

Generate a workflow graph::

    meandra graph mymodule:MyPipeline --output workflow.png


Next Steps
----------

- :doc:`concepts` - Core concepts and architecture
- :doc:`tutorials` - Step-by-step tutorials
- :doc:`../api/index` - API reference
