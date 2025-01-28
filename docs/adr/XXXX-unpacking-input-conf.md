# ADR 0001: Input Standardization and Configuration Unpacking Level

## Status

Proposed

## Context and Problem Statement

The workflow involves multiple components requiring inputs.
1. At which level should input arguments no longer be standardized?
   - Some components need structured input (e.g., `Node` expects a dictionary), while others might
     work best with raw arguments.

2. At which level should parameters be unpacked from the configuration object?
   - The system uses a hierarchical configuration management system.
   - Some components (e.g., Nodes) require very specific parameters, while others (e.g.,
     Orchestrator) may work with entire configuration sections.


## Decision Drivers

- **Clarity**: Ensure that each component has a well-defined role in managing parameters.
- **Modularity**: Prevent coupling between components by keeping parameter management within logical
  boundaries.
- **Flexibility**: Allow different workflow designs without enforcing a rigid structure.
- **Testing and Debugging**: Reduce the need to create additional mock objects.


## Considered Options

1. **Standardization Until Workflows**
   - Orchestrator → Scheduler → Workflow (receive standardized dictionaries).
   - Workflow extracts relevant parameters for each node and pass only the necessary ones.
   - Nodes receive only the minimal parameters they need for execution.

2. **Standardization Until Nodes**
   - Orchestrator → Scheduler → Workflow → Nodes (receive standardized dictionaries).
   - Nodes receive the full standardized dictionaries.
   - Each node extracts and processes the necessary configuration parameters internally (within
     their own `execute` method).


## Analysis of Options

1. **Standardized Inputs Until Workflows**
* Pros:
- Clarity: each node specifies the parameters and inputs it needs, according to its specific
  behavior.
- The workflow maintains control over parameter unpacking, ensuring a structured flow.
* Cons:
- Prevents a uniform interface across nodes.
- Workflows must be aware of node-specific configurations.

2. **Standardization Until Nodes**
* Pros:
- More modular nodes, which can be used in different workflows without modification.
- Better separation of concerns, as nodes manage their own inputs.
* Cons:
- Extra internal unpacking overhead in nodes, leading to potential redundancy.
- Boilerplate code to access parameters within the `execute` method.
- Coupling between nodes and configuration structure.


## Decision

**Chosen option**: (Option 2) Partial Standardization Until Nodes

**Justification**
- Nodes can be processed uniformly by the workflow, while still allowing for specific operations
  within the nodes.


## Consequences

### Future Implications

- Nodes should extract parameters in their `execute` method.
- Nodes can call more specific functions with raw parameters, thereby acting as a lower-level
  interface orchestrating more specific operations.
- Thereby, the processing functions themselves can manipulate the raw values instead of accessing
  them through the configuration object. They can define their own signature which reflect their
  specific behavior.
