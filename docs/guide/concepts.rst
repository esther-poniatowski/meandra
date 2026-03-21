Core Concepts
=============

This guide explains the fundamental concepts in Meandra.


Nodes
-----

A **node** is the basic unit of computation in a workflow. Each node:

- Has a **name** (unique within a workflow)
- Declares **inputs** it expects
- Declares **outputs** it produces
- May have **dependencies** on other nodes

.. code-block:: python

    @node(
        name="processor",
        inputs=["raw_data"],
        outputs=["processed_data"],
        depends_on=["loader"]
    )
    def process(inputs):
        data = inputs["raw_data"]
        return {"processed_data": transform(data)}


Workflows
---------

A **workflow** is a directed acyclic graph (DAG) of nodes. Workflows:

- Have a unique **name**
- Contain a collection of **nodes**
- Define execution order through **dependencies**

The workflow ensures nodes execute in the correct order based on their dependencies.


Pipelines
---------

A **pipeline** is a class-based workflow definition using decorators:

.. code-block:: python

    @pipeline(name="analysis")
    class AnalysisPipeline:
        @node(outputs=["data"])
        def load(self, inputs):
            ...

        @node(inputs=["data"], outputs=["result"], depends_on=["load"])
        def analyze(self, inputs):
            ...

Pipelines provide:

- **Encapsulation**: Group related nodes together
- **State**: Access instance attributes in nodes
- **Reusability**: Instantiate with different configurations

Build workflows with validation and constructor arguments:

.. code-block:: python

    workflow = build_workflow(
        AnalysisPipeline,
        init_args=("path/to/data.npy",),
        validate=True,
        available_inputs=set(),
    )


Orchestrators
-------------

An **orchestrator** executes workflows. Meandra provides:

- ``SchedulingOrchestrator``: Resolves dependencies and executes nodes in order

.. code-block:: python

    from meandra.orchestration import SchedulingOrchestrator

    orchestrator = SchedulingOrchestrator()
    result = orchestrator.run(workflow, initial_inputs)


Checkpoints
-----------

**Checkpoints** save intermediate results during workflow execution:

- Enable **resumption** after failures
- Reduce **recomputation** for long-running workflows
- Support **debugging** by inspecting intermediate states

Mark a node as checkpointable:

.. code-block:: python

    @node(outputs=["data"], checkpointable=True)
    def expensive_computation(inputs):
        ...


Data Catalog
------------

The **data catalog** manages dataset registration and I/O:

.. code-block:: python

    from meandra.datastore import DataCatalog

    catalog = DataCatalog()
    catalog.register("raw_data", "/path/to/data.npy")
    data = catalog.load("raw_data")


Contracts
---------

**Contracts** validate node inputs and outputs:

.. code-block:: python

    def validate_input(inputs):
        assert "data" in inputs
        assert len(inputs["data"]) > 0

    @node(
        inputs=["data"],
        outputs=["result"],
        input_contract=validate_input
    )
    def process(inputs):
        ...
