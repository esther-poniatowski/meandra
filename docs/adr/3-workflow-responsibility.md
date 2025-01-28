# ADR 0003: Workflow Responsibility

## Status

Accepted

## Context and Problem Statement

The role of a **workflow** within the library needs to be clearly defined, and distinct from other
components like nodes, orchestrator, scheduler.

- What should be the specific responsibilities of a workflow ?
- Which component should be in charge of dependency resolution ? Is it necessary to introduce
  schedulers, or workflows themselves can handle this functionality ?
- If a scheduler is introduced, should it be general across all the workflows or specific for
  different resolution approaches (and thus chosen by each workflow) ?
- Should workflows be responsible for the execution of their own nodes, or should they delegate this
  responsibility to the orchestrator ?


## Decision Drivers

- **Separation of Concerns**: Ensure workflows are not overloaded with too many responsibilities.
- **Modularity and Reusability**: Workflows should be composable, supporting nested sub-workflows.
  Maximize the reusability of components across different scenarios.
- **Scalability**: Support complex workflows with nested sub-workflows.
- **Flexibility**: Allow for different types of workflows and execution strategies.
- **Ease of Debugging and Monitoring**: Execution and dependency management should be trackable.


## Considered Options

1. **Workflows as Specifications**
- Workflows serve as central specifications of nodes, dependencies, inputs and outputs, checkpoints
  that define a specific processing run.
- They do not execute themselves (they do not provide an `execute` method). Instead they delegate
  this responsibility to the orchestrator, which reads the workflow and executes nodes accordingly.
- If a workflow contains sub-workflows, the scheduler recursively unpacks the nodes to determine a
  global execution order for the entire workflow.

2. **Workflows as Actors**
- Workflows resolve the dependencies between their nodes to determine their execution order.
- Workflows are responsible for the execution of their nodes, i.e. manages the lifecycle of its
  execution.

3. **Hybrid Workflows**
- Workflows are responsible for the resolution of dependencies between their nodes.
- Workflows delegate the execution of their nodes to the orchestrator.
- The scheduler is optional and can be workflow-specific or general.


## Analysis of Options

1. **Workflows as Specifications**
* Pros:
  - Separation of Concerns between workflow definition and execution: Workflows remain purely
    declarative, they specify structure but do not manage execution.
  - Modularity: Since execution is centralized in the orchestrator, workflows remain lightweight and
    reusable.
  - Debugging: The orchestrator can provide centralized logging and monitoring.
  - Scalability: The orchestrator can handle parallelization, checkpointing, and failure recovery in
    a centralized manner.
  - Flexibility: Workflows do not impose a *fixed* dependency resolution strategy, allowing multiple
    schedulers to be introduced.
* Cons:
  - Extra Layer of Indirection: Requires the orchestrator to manage workflow execution.
  - Dependency on the Orchestrator: Workflows cannot function without the orchestrator component.
  - Extra Component: Introduces an orchestrator and a scheduler, which may add complexity to the
    system.

2. **Workflows as Actors**
* Pros:
  - Encapsulation: Each workflow controls its own execution, making it self-contained.
  - Autonomy: Workflows can execute independently.
* Cons:
  - Less Reusability: Workflows tightly couple dependency resolution and execution, making them
    harder to reuse.
  - Potential Code Duplication: Workflows may duplicate execution logic.
  - Complexity: Each workflow has to handle execution logic, making the design less scalable.
    Tracking execution is harder, as workflows operate independently.

3. **Hybrid Workflows**
* Pros:
  - Balance between control and responsibility: Allows workflows to define their structure while
    delegating execution.
  - Flexibility: Allows workflows to choose their own schedulers.
* Cons:
  - Blurs Separation of Concerns: Mixing dependency resolution with workflow logic can create tight
    coupling.
  - Complexity: Workflows now manage both execution planning *and* interaction with the
    orchestrator.


## Decision

**Chosen option**: 1. **Workflows as Specifications**

**Justification**:
- Clearest separation of concerns, making the system more modular and maintainable.
- Centralized execution logic: Improves scalability, debugging, and tracking, optimization and
  parallelization.
- Reusability: Workflow only *define data flow* without enforcing execution strategy, making them
  adaptable.
- Scalability: Easily handle nested workflows by recursively unpacking them.
- The use of a general scheduler across all workflows ensures consistency and reusability.


## Future Implications

- Implement communication between components.
- Create clear interfaces for workflows to define their structure and dependencies.
- Use a *general* scheduling mechanism within the orchestrator, allowing different resolution
  strategies.


## Links
- [Airflow's approach to workflow definition](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html)
- [Luigi's Task model](https://luigi.readthedocs.io/en/stable/tasks.html)
