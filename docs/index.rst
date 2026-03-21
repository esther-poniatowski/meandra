Meandra Documentation
=====================

Meandra is a workflow orchestration library for building robust, modular data analysis pipelines.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guide/quickstart
   guide/concepts
   guide/tutorials
   api/index
   architecture/index


Quick Example
-------------

Define a pipeline using decorators::

    from meandra.api import pipeline, node, build_workflow

    @pipeline(name="data_pipeline")
    class DataPipeline:
        @node(outputs=["data"])
        def load(self, inputs):
            return {"data": [1, 2, 3, 4, 5]}

        @node(inputs=["data"], outputs=["result"], depends_on=["load"])
        def process(self, inputs):
            return {"result": sum(inputs["data"])}

    workflow = build_workflow(DataPipeline, validate=True, available_inputs=set())

Or use the fluent API::

    from meandra.api import step, pipe

    workflow = (
        pipe("data_pipeline")
        .add(step(load_data).out("data"))
        .add(step(process).in_("data").out("result").depends_on("load_data"))
        .build()
    )


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
