# ADR 0001: Input Standardization and Configuration Unpacking Level

**Status**: Accepted

---

## Problem Statement

The workflow involves multiple components requiring inputs:
- Some components need structured input (e.g., `Node` expects a dictionary), while others might work
  best with raw arguments.
- The system uses a hierarchical configuration management system. Some components (e.g., Nodes)
  require very specific parameters, while others (e.g., Orchestrator) may work with entire
  configuration sections.

**Questions to be addressed**:
1. Standardization: At which level should input arguments no longer be standardized?
2. Parameter unpacking: At which level should parameters be unpacked from the configuration object?

---

## Decision Drivers

- **Clarity**: Ensure that each component has a well-defined role in managing parameters.
- **Modularity**: Minimize coupling between components by keeping parameter management within
  logical boundaries. Components should be reusable in different workflows without depending too
  much on the components which manage configuration.
- **Flexibility**: Allow different workflow designs without enforcing a rigid structure.
- **Testing and Debugging**: Reduce the need to create additional mock objects.

---

## Considered Options

1. **Standardization Until Workflows**
   - Orchestrator, Scheduler, and Workflow receive standardized dictionaries.
   - Workflow extracts relevant parameters for each node and passes only the necessary ones.
   - Nodes receive only the minimal parameters they need for execution.

```python
# Workflow implementation
def execute(self, standardized_input):
    node_params = self.extract_node_params(standardized_input)
    for node in self.nodes:
        node.execute(node_params[node.id])
```

2. **Standardization Until Nodes**
   - Orchestrator, Scheduler, Workflow, and Nodes receive standardized dictionaries.
   - Nodes receive the full standardized dictionaries.
   - Each node extracts and processes the necessary configuration parameters internally (within
     their own `execute` method).

```python
# Node implementation
def execute(self, standardized_input):
    params = self.extract_params(standardized_input)
    self.process(params['param1'], params['param2'])
```

---

## Analysis of Options

### Individual Assessment

1. **Standardization Until Workflows**
* Pros:
  - Clarity: Each node specifies the parameters it needs, according to its specific behavior.
  - Structure and Automation: The workflow maintains control over parameter unpacking.
* Cons:
  - Consistency: Prevents a uniform interface across nodes, potentially coupling workflows to
    node-specific configurations.
  - Decoupling: Workflows must be aware of node-specific configurations, limiting their
    adaptability.

2. **Standardization Until Nodes**
* Pros:
  - Modularity: Nodes can be used in different workflows without modification.
  - Clarity: Nodes manage their own inputs, providing a clear separation of concerns.
* Cons:
  - Efficiency: Extra internal unpacking in each node may introduce some overhead.
  - Clarity: Access to parameters within the `execute` method requires additional code, potentially
    reducing readability.
  - Decoupling: Nodes should explicitly manipulate the configuration object.


### Summary: Comparison by Criteria

- **Modularity**
  - **Standardization Until Workflows**: LOW (workflow-node coupling)
  - **Standardization Until Nodes**: HIGH (independent node configuration)

- **Clarity**
  - **Standardization Until Workflows**: MEDIUM (clear node requirements, but complex workflow
    logic)
  - **Standardization Until Nodes**: HIGH (clear separation of concerns)

- **Flexibility**
  - **Standardization Until Workflows**: LOW (rigid workflow-node relationship)
  - **Standardization Until Nodes**: HIGH (adaptable to different workflow designs)

- **Testability**
  - **Standardization Until Workflows**: MEDIUM (easier workflow testing, but complex node mocking)
  - **Standardization Until Nodes**: HIGH (simplified unit testing for nodes)

---

## Conclusions

### Decision

**Chosen option**: 2. Standardization Until Nodes

**Justification**: This option provides superior modularity and flexibility, allowing nodes to be
processed uniformly by workflows while maintaining their ability to handle specific operations
internally.

**Discarded options**:
- **Standardization Until Workflows**: Rejected due to reduced modularity and flexibility, which
  could lead to tighter coupling between workflows and nodes.


### Final Answers

1. Input arguments should be standardized until they reach the nodes.
2. Parameters should be unpacked from the configuration object within each node's `execute` method.

---

## Implications

- Nodes must implement parameter extraction logic in their `execute` method.
- Nodes will act as lower-level interfaces, orchestrating more specific operations with raw
  parameters.
- Processing functions within nodes can manipulate raw values instead of accessing them through the
  configuration object, allowing for more specific function signatures.
