# ADR 0004: Workflow Creation

## Status

Proposed

## Context and Problem Statement

The precise nature of **workflows** needs to be determined.

1. **What defines a workflow class vs. a workflow instance?**
  - What differentiates multiple workflow **classes** from each other? Is it even necessary to
    define multiple workflow classes?
  - What differentiates multiple **instances** of the same workflow class?

Workflows are primarily characterized by the types of nodes they include and the parameters of those
nodes (e.g. input-output data). However, distinct workflow types usually have predictable node type
sequences. Within a given workflow, variations between instances are rather related to the number of
nodes and the parameters of those nodes.

Thus, two levels of structure and configuration can be identified:
- The general structure of a workflow type, which determines the types of nodes to be included.
- The specific configuration of each workflow instance, which determines the number of nodes and
  their parameters.

2. **Which component is responsible for creating workflows?**
  - Should workflows **instantiate themselves**, or should a **dedicated creator** class be
    responsible for creation?
  - Specifically, the identity of the nodes in a workflow is determined at runtime based on
    configuration. It involves generating nodes with many parameters and adding them to the
    workflow. What is the best approach to handle this complex creation process?


## Decision Drivers

- **Configurability**: Support defining multiple workflow types while allowing dynamic
  instance-specific configuration, especially for the nodes it contains.
- **Reusability**: Uniformize workflow creation, without tight coupling to specific instantiation
  logic.
- **Extensibility**: If necessary in the future, support different workflow creation strategies
  without introducing rigid constraints.
- **Clarity**: Clear process to define workflows without too much complexity or indirection, and
  boilerplate code.


## Considered Options

1. **Workflow Self-Creation with a Static Factory Method**
  - A workflow class offers a factory method to create instances (`create()` or `from_config()`).
  - At runtime, the workflow class generates the attributes based on a configuration to create an
    instance.
  - If different workflow creation approaches are required, multiple factory methods can be
    implemented.

Implementation 1: Static factory method with multiple factory methods.
```python
class WorkflowA(Workflow):
    @staticmethod
    def from_config(config):
        nodes = [ Node1(**params) for params in config["nodes1"]]
        if config["user_input"] :
            nodes.append(Node2(**config["nodes2"][0]))
        return ProcessingWorkflow(nodes)

class WorkflowB(Workflow):
    @staticmethod
    def from_config(config):
        nodes = [Node3(**params) for params in config["nodes3"]]
        return AnalysisWorkflow(nodes)

# Instantiate workflows
config_A = {"nodes1": [{"factor": 2}, {"factor": 3}], "nodes2": [{"value": 10}]}
workflow_A = WorkflowA.from_config(config_A)

config_B = {"nodes3": [{"arg": 20}]}
workflow_B = WorkflowB.from_config(config_B)
```

Implementation 2: Static factory method with a single factory method and workflow types predefined
in the configuration.
```python
class Workflow:
    def __init__(self, nodes):
        self.nodes = nodes

    @staticmethod
    def from_config(config):
        """Create a workflow instance based on configuration"""
        workflow_types = {
            "workflow_A": [
                {"type": "node1", "repeat": True},
                {"type": "node2", "condition": "user_input"},
            ],
            "workflow_B": [
                {"type": "node3", "repeat": True}
            ],
        }
        nodes = []
        for node_spec in workflow_types[config["workflow_type"]]:
            node_class = {"node1": Node1, "node2": Node2, "node3": Node3}[node_spec["type"]]
            if node_spec.get("repeat", False):
                nodes.extend([node_class(**params) for params in config["nodes"].get(node_spec["type"], [])])
            elif node_spec.get("condition") and config.get(node_spec["condition"], False):
                nodes.append(node_class(**config["nodes"].get(node_spec["type"])[0]))
        return Workflow(nodes)

# Instantiate workflows
config_A = {"workflow_type": "workflow_A", "nodes": {"node1": [{"factor": 2}, {"factor": 3}], "node2": [{"value": 10}]}, "user_input": True}
config_B = {"workflow_type": "workflow_B", "nodes": {"node3": [{"arg": 20}]}}

workflow_A = Workflow.from_config(config_A)
workflow_B = Workflow.from_config(config_B)
```

Implementation 3: Static factory method with a single factory method and number od nodes predefined
in the configuration.
```python
class Workflow:
    def __init__(self, nodes):
        self.nodes = nodes

    @staticmethod
    def from_config(config):
        node_types = {
            "node1": Node1,
            "node2": Node2,
            "node3": Node3,
        }
        nodes = []
        for node_config in config["nodes"]:
            node_type = node_types[node_config["type"]]
            if "condition" in node_config:
                if eval(node_config["condition"], config):
                    nodes.append(node_type(**node_config["params"]))
            else:
                nodes.append(node_type(**node_config["params"]))
        return Workflow(nodes)

# Instantiate workflows
config_A = {
    "nodes": [
        {"type": "node1", "params": {"factor": 2}},
        {"type": "node1", "params": {"factor": 3}},
        {"type": "node2", "params": {"value": 10}, "condition": "user_input"}
    ],
    "user_input": True
}
workflow_A = Workflow.from_config(config_A)
```

2. **Workflow Self-Configuration with Setter Methods**
  - A workflow class offers setter methods to update its attributes (`add_node` , `set_attr`) and a
    central method to configure itself from a configuration object (`configure()`).
  - At runtime, the workflow class reads the configuration and sets its attributes accordingly.
  - If different workflow creation approaches are required, multiple configuration methods can be
    implemented.

Implementation 1: Setter methods with multiple configuration methods.
```python
class WorkflowA(Workflow):
    def configure(self, config):
        for params in config["nodes1"]:
            self.add_node(Node1(**params))
        if config["user_input"]:
            self.add_node(Node2(**config["nodes2"][0]))

class WorkflowB(Workflow):
    def configure(self, config):
        for params in config["nodes3"]:
            self.add_node(Node3(**params))

# Instantiate workflows
workflow_A = WorkflowA()
workflow_A.configure(config_A)

workflow_B = WorkflowB()
workflow_B.configure(config_B)
```

Implementation 2: Setter methods with a single configuration method.
```python
class Workflow:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def configure(self, config):
        workflow_types = {
            "workflow_A": [
                {"type": "node1", "repeat": True},
                {"type": "node2", "condition": "user_input"},
            ],
            "workflow_B": [
                {"type": "node3", "repeat": True}
            ],
        }
        for node_spec in workflow_types[config["workflow_type"]]:
            node_class = {"node1": Node1, "node2": Node2, "node3": Node3}[node_spec["type"]]
            if node_spec.get("repeat", False):
                for params in config["nodes"].get(node_spec["type"], []):
                    self.add_node(node_class(**params))
            elif node_spec.get("condition") and config.get(node_spec["condition"], False):
                self.add_node(node_class(**config["nodes"].get(node_spec["type"])[0]))

# Instantiate workflows
workflow_A = Workflow()
workflow_A.configure(config_A)

workflow_B = Workflow()
workflow_B.configure(config_B)
```

3. **Workflow Factory**
  - A general factory creates *all* workflow instances (`WorkflowFactory`).
  - At runtime, the factory takes configuration to instantiate the correct workflow.
  - If different workflow creation approaches are required, multiple factories can be implemented.

Implementation 1: Single factory with multiple creation methods.
```python
class WorkflowFactory:
    def create_workflow_A(self, config):
        workflow = Workflow()
        for params in config["nodes1"]:
            workflow.add_node(Node1(**params))
        if config["user_input"]:
            workflow.add_node(Node2(**config["nodes2"][0]))
        return workflow

    def create_workflow_B(self, config):
        workflow = Workflow()
        for params in config["nodes3"]:
            workflow.add_node(Node3(**params))
        for params in config["nodes4"]:
            workflow.add_node(Node4(**params))
        return workflow

factory = WorkflowFactory()
workflow_A = factory.create_workflow_A(config_A)
workflow_B = factory.create_workflow_B(config_B)
```

Implementation 2: Single factory with a single creation method.
```python
class WorkflowFactory:
    def create_workflow(config):
        workflow = Workflow()
        workflow_types = {
            "workflow_A": [
                {"type": "node1", "repeat": True},
                {"type": "node2", "condition": "user_input"},
            ],
            "workflow_B": [
                {"type": "node3", "repeat": True}
            ],
        }
        node_types = {"node1": Node1, "node2": Node2, "node3": Node3}
        for node_spec in workflow_types[config["workflow_type"]]:
            node_class = node_types[node_spec["type"]]
            if node_spec.get("repeat", False):
                for params in config["nodes"].get(node_spec["type"], []):
                    workflow.add_node(node_class(**params))
            elif node_spec.get("condition") and config.get(node_spec["condition"], False):
                workflow.add_node(node_class(**config["nodes"].get(node_spec["type"])[0]))
        return workflow

# Instantiate workflows
workflow_A = WorkflowFactory.create_workflow(config_A)
workflow_B = WorkflowFactory.create_workflow(config_B)
```


4. **Workflow Builders with Director**
  - Use the Builder pattern to construct complex workflows.
  - A Director class coordinates the building process.
  - If different workflow creation approaches are required, multiple builders can be implemented.

Implementation 1: Workflow Builders with Director.
```python
class WorkflowBuilder:
    def __init__(self):
        self.workflow = Workflow()

    def add_node(self, node):
        self.workflow.nodes.append(node)

    def get_workflow(self):
        return self.workflow

class WorkflowABuilder(WorkflowBuilder):
    def build_nodes_1(self, config):
        for params in config["nodes1"]:
            self.workflow.add_node(Node1(**params))

    def build_nodes_2(self, config):
        self.workflow.add_node(Node2(**config["nodes2"][0]))


class WorkflowBBuilder(WorkflowBuilder):
    def build_nodes_3(self, config):
        for params in config["nodes3"]:
            self.workflow.add_node(Node3(**params))

class WorkflowDirector:
    def construct_workflow_A(self, builder, config):
        builder.build_nodes_1(config)
        if config["user_input"]:
            builder.build_nodes_2(config)
        return builder.get_workflow()

    def construct_workflow_B(self, builder, config):
        builder.build_nodes_3(config)
        return builder.get_workflow()

director = WorkflowDirector()
builder_A = WorkflowABuilder()
builder_B = WorkflowBBuilder()

workflow_A = director.construct__workflow_A(builder_A, config_A)
workflow_B = director.construct__workflow_B(builder_B, config_B)
```

Implementation 2: Workflow Builders with Director (Generic).
```python
class WorkflowBuilder:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def get_workflow(self):
        return Workflow(self.nodes)

class WorkflowDirector:
    def __init__(self, builder):
        self.builder = builder

    def construct_workflow(self, config):
        workflow_types = {
            "workflow_A": [
                {"type": "node1", "repeat": True},
                {"type": "node2", "condition": "user_input"},
            ],
            "workflow_B": [
                {"type": "node3", "repeat": True}
            ],
        }
        node_types = {"node1": Node1, "node2": Node2, "node3": Node3}
        for node_spec in workflow_types[config["workflow_type"]]:
            node_class = node_types[node_spec["type"]]
            if node_spec.get("repeat", False):
                for params in config["nodes"].get(node_spec["type"], []):
                    self.builder.add_node(node_class(**params))
            elif node_spec.get("condition") and config.get(node_spec["condition"], False):
                self.builder.add_node(node_class(**config["nodes"].get(node_spec["type"])[0]))

        return self.builder.get_workflow()

# Using director to construct workflows
builder = WorkflowBuilder()
director = WorkflowDirector(builder)

workflow_A = director.construct_workflow(config_A)
workflow_B = director.construct_workflow(config_B)
```

## Analysis of Options

1. **Workflow Self-Creation with a Static Factory Method**
* Pros:
  - Valid if workflows are simple and configuration-driven.
  - Efficient when a workflow can be initialized in one step from a configuration.
* Cons:
  - Limited Flexibility: Harder to customize once created.
  - Complexity: Can lead to large, monolithic constructors if workflows have complex dependencies.
  - Breaks the Single Responsibility Principle: workflows are responsible for their own creation.

2. **Workflow Self-Configuration with Setter Methods**
* Pros:
  - Valid when workflows evolve dynamically over time (e.g., incremental node addition).
  - Flexibility: More flexible than a factory method, since it allows incremental configuration.
* Cons:
  - Complexity: Risks polluting the API with too many setters.
  - Inconsistency: Nodes might be added in an inconsistent state.
  - Encourages mutability, which might not be ideal for well-defined, immutable workflows.

3. **Workflow Factory**
* Pros:
  - Valid if workflows need centralized creation logic.
  - Centralized Creation: Single entry point for creating workflows.
  - Separation of Concerns: Keeps workflow instances clean by delegating instantiation.
  - Flexibility: The factory can instantiate workflows from different sources.
* Cons:
  - Complexity: Requires an extra step to instantiate workflows. Factories are only justified if
    workflows are complex.
  - Coupling: If not designed properly, the factory might be tightly coupled to specific workflow
    types.

4. **Workflow Builders with Director**
* Pros:
  - Valid for complex workflows with multiple configuration stages.
  - Separation of Concerns: Builders encapsulate the construction process.
  - Flexibility: Allows step-by-step creation and validation.
* Cons:
  - Complexity: Overhead for simple workflows, since both a builder and director are needed.
  - Potential Overhead: Requires additional classes and methods to manage the building process.


### Comparison by Criteria

- **Flexibility - Configurability**
  - Static Factory Method: Low
  - Setter-Based Configuration: Medium
  - Workflow Factory: High
  - Builder + Director: Very high
- **Reusability**
  - Static Factory Method: Limited
  - Setter-Based Configuration: Limited
  - Workflow Factory: High
  - Builder + Director: High
- **Maintainability**
  - Static Factory Method: Limited (harder to modify)
  - Setter-Based Configuration: Limited (risk of inconsistent states)
  - Workflow Factory: Satisfying (centralized control)
  - Builder + Director: Satisfying (step-by-step construction)
- **Extensibility - Scalability**
  - Static Factory Method: Low
  - Setter-Based Configuration: Medium (harder to manage at scale)
  - Workflow Factory: High (easy to extent)
  - Builder + Director: Very high (best for complex workflows)
- **Complexity**
  - Static Factory Method: Low
  - Setter-Based Configuration: Higher (requires setters)
  - Workflow Factory: Moderate
  - Builder + Director: Very high
- **Separation of Concerns**
  - Static Factory Method: No (workflows handle their own creation)
  - Setter-Based Configuration: No (workflows still configure themselves)
  - Workflow Factory: Clean separation
  - Builder + Director: Full encapsulation

### Best Use Cases

- **Static Factory Method**: Simple, configuration-driven workflows that do not require much
  customization.
- **Setter-Based Configuration**: Dynamically evolving workflows that need incremental
  configuration.
- **Workflow Factory**: Complex workflows with centralized creation logic that require different
  workflow types.
- **Builder + Director**: Highly complex workflows with multiple configuration stages that need
  step-by-step construction.


## Decision

**Chosen option**: Workflow Factory

**Justification**:
  - **Balances flexibility and structure**: Allows dynamic workflow instantiation while keeping
    workflow classes lightweight.
  - **Extensibility**: Additional workflow types or node variations can be added without
    modifying existing workflow logic.
  - **Maintainability**: **Centralized** instantiation logic allows for consistent instantiation and
    reduces redundant code across workflow definitions.
  - **Separation of concerns**: Creation logic is handled outside the workflow class, maintaining
    modularity.
  - **Testing**: Factories enable **mocking and dependency injection**, simplifying **unit
    testing**.

While the Builder with Director pattern offers the highest flexibility and extensibility, it may
introduce unnecessary complexity for most scenarios.

The Static Factory Method and Setter Methods approaches may not provide enough flexibility for
managing complex workflow configurations.


## Future Implications

- Implement a robust and flexible factory class capable of creating various workflow types. Define
  clear interfaces for adding new workflow types without modifying existing factory code.
- Develop a **standardized configuration format** for different workflows.
- Potential need for a registry or plugin system: If workflows expand significantly, a **registry**
  (mapping workflow names to classes) might be needed. It would allow dynamic discovery and loading of
  **new workflow types** at runtime.
