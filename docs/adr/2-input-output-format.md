# ADR 0002: Input-Output Format

**Status**: Proposed

---

## Problem Statement

What should be the format of inputs and outputs for node execution methods (e.g., `execute`)?

**Questions to be addressed**:
1. How should nodes exchange data in a structured, type-safe, and interoperable manner?
2. How can the input/output format integrate with checkpointing mechanisms for workflow persistence?

---

## Decision Drivers

- **Consistency**: Ensure the input/output format is compatible across different components.
  - In linear workflows, a node’s output must match the expected input of subsequent nodes.
  - In checkpoints workflows, the format must align with data storage and retrieval mechanisms (data
    catalog, IO handlers).
- **Flexibility**: Support diverse data types without imposing unnecessary constraints.
- **Readability**: Provide an intuitive and clear interface for defining and interacting with inputs
  and outputs.
- **Performance**: Avoid introducing significant computational overhead for data conversion.

---

## Considered Options

1. **Dictionary with string keys and arbitrary values**
Each node receives and returns a dictionary:

```python
def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    x = inputs['x']
    y = inputs['y']
    return {'z': x + y, 'w': x - y}
```

2. **Keyword arguments for inputs and tuple for outputs**
Each node receives its input as keyword arguments and returns a tuple:
   - Uses function signature to specify expected arguments.
   - Returns a tuple, relying on position rather than named attributes.

```python
def execute(self, *, x: float, y: float) -> Tuple[float, float]:
    return x + y, x - y
```

3. **Structured object (Dataclass or custom class)**
Each node receives and returns an instance of a structured object:

```python
@dataclass
class NodeInput:
    x: float
    y: float

@dataclass
class NodeOutput:
    z: float
    w: float

def execute(self, inputs: NodeInput) -> NodeOutput:
    z = inputs.x + inputs.y
    w = inputs.x - inputs.y
    return NodeOutput(z=inputs.x + inputs.y, w=inputs.x - inputs.y)
```

## Analysis of Options

### Individual Assessment

1. **Dictionary with string keys and any values**
* Pros:
  - Flexibility: Can hold heterogeneous data structures.
  - Extensibility: New parameters can be added without modifying function signatures.
  - Consistency: Uniform format for both input and output.
  - Complexity: Straightforward to implement and use.
  - Efficiency: Easily serializable for storing intermediate results.
* Cons:
  - Robustness: Requires additional checks to ensure expected keys are present, and dictionaries do
    not enforce a strict schema.
  - Style: Requires manual key-based access to input/output values within the function and creating
    a new dictionary for output.
  - Documentation: Requires additional documentation of expected keys and value types.

2. **Keyword arguments for inputs and tuple for outputs**
* Pros:
  - Readability: Function signatures explicitly define expected inputs/outputs and their types. More
    Pythonic approach for function calls.
  - Style: Parameters are directly accessible by name within the function.
  - Robustness: Enforces type hints for inputs and outputs.
  - Flexibility: Supports default values for optional parameters.
  - Usability: Easier to work with in an Integrated Development Environment.
* Cons:
  - Flexibility: Adding/removing parameters requires modifying all function signatures.
  - Consistency: Different nodes may have different numbers of inputs/outputs, which prevents a
    uniform interface for the `execute` method.
  - Complexity: Checkpoint storage and retrieval must be adapted to tuple-based outputs.
  - Explicitness: Output names are lost when returning, which makes it harder to identify what each
    value represents.

3. **Structured object (Dataclass or custom class)**
* Pros:
  - Robustness: Each input/output follows a defined schema which is associated with the node, which
    prevents missing inputs and outputs. Robust specification of expected inputs and outputs and
    constraints (e.g. pydantic).
  - Readability: Named attributes clarify input/output semantics.
  - Style: Input values are accessible by the dot notation instead of dictionary keys.
  - Documentation: Clearly defines expected input/output fields in the custom object which stores
    inputs or outputs.
* Cons:
  - Complexity: Every node requires a unique dataclass. More complex to implement and maintain.
  - Efficiency: Requires extra conversion steps to serialize/deserialize structured objects.


### Summary: Comparison by Criteria

- **Consistency**
  - **Dictionary**: Medium (relies on key-based consistency)
  - **Keyword arguments**: Low (inconsistent across nodes)
  - **Structured object**: High (explicit and enforced schema)

- **Interoperability**
  - **Dictionary**: High (easily serializable and flexible)
  - **Keyword arguments**: Low (tuple outputs are harder to integrate with checkpointing)
  - **Structured object**: High (schema-based integration with checkpointing systems)

- **Flexibility**
  - **Dictionary**: High (dynamic structure allows adaptability)
  - **Keyword arguments**: Low (rigid function signatures)
  - **Structured object**: Medium (requires predefined schemas but can support evolution)

- **Readability & Maintainability**
  - **Dictionary**: Low (key-based access increases risk of errors)
  - **Keyword arguments**: High (explicit function signatures)
  - **Structured object**: High (clearly defined attributes and types)

- **Performance**
  - **Dictionary**: Medium (overhead from key lookups and dictionary creation)
  - **Keyword arguments**: High (direct attribute access)
  - **Structured object**: Medium (minor overhead from object instantiation)

---

## Conclusions

### Decision

**Chosen option**: 3. **Structured object (Dataclass or custom class)**

**Justification**:
- Provides structured, type-safe interfaces for inputs and outputs. It aligns well with the concept
  of nodes as self-contained entities with well-defined interfaces.
- Allows for integration with validation libraries like Pydantic.
- Enhances maintainability and readability by explicitly defining expected fields and offering a
  central place for documentation.
- Facilitates validation and serialization, ensuring compatibility with checkpointing.

**Justification**:
- Option 2 is eliminated due to its inflexibility and inconsistency.
- Option 1 is eliminated due to:


**Discarded options**:
- **Dictionary**:
  - Lack of structure and type safety.
  - Need for manual validation and documentation of expected keys.
  - Overhead of key-based access and dictionary creation.
- **Keyword arguments with tuple outputs**: Lack of type safety and structured validation.


### Final Answers

1. **How should nodes exchange data?**
   - Through structured input and output objects that define clear attributes.
2. **How can the format integrate with checkpointing?**
   - By implementing serialization methods for structured objects, ensuring compatibility with storage systems.

---

## Implications

### Next Steps

- Decide which structure object is the most appropriate. Consider integrating runtime validation
  (e.g., Pydantic) to enforce key presence and types while keeping a dictionary-based approach.
- Implement interaction with the IO handler to accept and provide data depending on the node which
  requests it.
- Introduce a conversion layer to make compatible with serialization.

### Suggestions to Improve the Implementation

**Mitigate Boilerplate Overhead**
- Instead of writing a dataclass for every node, introduce a generic base class for input/output
  objects.
- Then each node’s input/output class can extend the base class by adding specific fields.
- This provides a structured interface but also allows conversion to/from dictionaries, easing
  serialization and interfacing with the data catalog.

```python
from dataclasses import dataclass
from typing import Dict, Any

# Base class for node inputs and outputs
@dataclass
class NodeData:
    """Base class for node inputs and outputs"""
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

# Concrete node input/output classes
@dataclass
class AddNodeInput(NodeData):
    x: float
    y: float

@dataclass
class AddNodeOutput(NodeData):
    z: float
    w: float
```

**Serialization Strategy**
- Implement a unified serialization mechanism inside the IO handler, so that structured objects
    automatically serialize/deserialize when stored in checkpoints. This ensures structured objects
    can be checkpointed efficiently without breaking compatibility, and that checkpointed data is
    converted back into structured objects before passing them into nodes.
- Decouple serialization from nodes: The IO handler should transparently handle storage and
  retrieval.
```python
import json

class IOHandler:
    @staticmethod
    def save(key: str, data: NodeData):
        with open(f"{key}.json", "w") as f:
            json.dump(data.to_dict(), f)

    @staticmethod
    def load(cls, key: str) -> NodeData:
        with open(f"{key}.json", "r") as f:
            return cls.from_dict(json.load(f))
```

---

## See Also

### Related Decisions

- [ADR-0001](./0001-example.md): Relates to workflow execution models.

### References and Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Dataclasses in Python](https://docs.python.org/3/library/dataclasses.html)
