Steps in a workflow :
1. The user passes the name of the workflow to run, and any other overrides, to the CLI.
2. The configuration files are loaded : the base default file, the file associated with the workflow
   (or a custom file passed by the user).
3. The configuration object is created by merging all the sources.
4. The workflow is created dynamically to include the appropriate nodes based on runtime conditions.
5. Dependencies are resolved to determine the order in which nodes should be executed.
6. The workflow is executed. Each node leads to the following steps:
    1. The logger or state tracker reports the node is starting.
    2. Inputs required by the node are identified from the data catalog.
    3. Data is loaded using the approach appropriate for the input format. This occurs outside of
       the node, and the data is passed to the node as an argument.
    4. The node is executed.
    5. The node outputs are saved based on the specifications of the data catalog.
    6. The logger or state tracker reports the node is finished and the outputs are saved.
7. The workflow is finished. The logger or state tracker reports the workflow is finished and saves
   the logs in the appropriate location.

---

Defining Nodes
- How nodes should be initialized when they are added to the workflow ? Specifically, what
  attributes are necessary to define a node, that will be useful for the following steps ?
- What defines a node class vs. a node instance ? What differentiates several node classes from
  each other ? What differentiates several node instances of the same class from each other ?

Specifying Inputs
- How should the link between the nodes inputs and the catalog be made ? Should the nodes
  themselves be aware of the keys of their inputs in the catalog ? Or should they only receive a
  structured input and let other components handle the resolution of the keys ?
- Where should this specification be stored ? In the node itself or in the configuration object ?

Specifying Dependencies
- Should the dependencies between nodes be defined in the workflow or in the nodes themselves ?
  If it is in the nodes, how should the workflow be aware of them ?
Dependencies should be defined at the moment of workflow definition. Nodes remain agnostic to the
specific context in which they are run. They focus on their computational logic. Or at least, those
attributes are instance attributes that should be initialized when the node instance is added to a
workflow. However the computation performed by the node defines the class.

Node execution
- Which component should be in charge of this ? The orchestrator, the workflow or the node itself ?

Maybe I should define a dynamic data registry. It will generate keys even for intermediate data.

- If some workflow do not require io operations, they still define names for intermediate data which
will flow across nodes.
- If a workflow needs to access and save data on the disk, it will resolve the paths based on the
catalog. Moreover, it will generate an arbitrary number of paths dynamically if a full directory is
scanned.
- If a workflow requires checkpoints, it will generate temp paths automatically without requiring
specifying those intermediate data in the catalog.
- If a workflow requires caching,

I should find a way to link to the data catalog.

What is defined outside the orchestrator ? Where does it start and and ?

It should accept the catalog, the data provider the scheduler, the logger. 
- Option 1. Pass the objects with already resolved paths, keys ad dependencies. Thereby the
  orchestrator is ready to run, and it can focus on the execution sequence. And it is more maniable for testing, since an arbitrary order can be passed.
- Option 2. Resolve as the first step. This ensures consistency with the content of the
  workflow.Maybe the scheduler can set the order within the workflow. Thereby there is one object
  less to pass to the orchestrator. Or should the workflow accept a scheduler ?
