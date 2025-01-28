# ADR 0002: Input-Output Format

## Status

Proposed

## Context and Problem Statement

What should be the format of inputs and outputs of nodes (e.g. the `execute` method)?


## Decision Drivers

- **Consistency**: Nodes in a linear workflow pass data sequentially, so their output format must
   be compatible with the next node's input.
- **Checkpoint Compatibility**: If a workflow uses checkpoints, inputs and outputs must align with
   the data catalog and IO handler, where data is identified by unique keys.
- **Flexibility**: The format should be flexible enough to accommodate different types of data.

## Decision Drivers

- **Interoperability**: The input/output format should be compatible across different components.
  - In linear workflows, a node’s output **must match** the expected input of subsequent nodes.
  - In checkpointed workflows, the format must align with **data storage and retrieval mechanisms**.
- **Flexibility**: The format should support different data types without unnecessary constraints.
- **Readability & Maintainability**: The format should be **intuitive** and easy to debug.
- **Performance**: Should not introduce excessive overhead in conversions.


## Considered Options

1. **Dictionary with string keys and any values**
Each node receives and returns a dictionary:
```python
def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    x = inputs['x']
    y = inputs['y']
    z = x + y
    w = x - y
    return {'z': z, 'w': w}
```

2. **Keyword arguments for inputs and tuple for outputs**
Each node receives its input as keyword arguments and returns a tuple:
```python
def execute(self, *, x: float, y: float) -> Tuple[float, float]:
    z = x + y
    w = x - y
    return z, w
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
    return NodeOutput(z=z, w=w)
```


## Analysis of Options

1. **Dictionary with string keys and any values**
* Pros:
  - Flexible: Can hold heterogeneous data structures.
  - Consistency: Uniform format for both input and output.
  - Simplicity: Straightforward to implement and use.
  - Checkpoint compatibility: Easily serializable for storing intermediate results.
  - Dynamic expansion: New parameters can be added without modifying function signatures.
* Cons:
  - No Direct Validation: Requires additional checks to ensure expected keys are present.
  - Less Type Safety: Dictionaries do not enforce a strict schema.
  - Overhead: Requires manual key-based access to input/output values within the function and
    creating a new dictionary for output.
  - Documentation: Requires additional documentation of expected keys and value types.

2. **Keyword arguments for inputs and tuple for outputs**
* Pros:
  - Readability: Function signatures explicitly define expected inputs/outputs and their
    types. More Pythonic approach for function calls.
  - Access: Parameters are directly accessible by name within the function.
  - Type Safety: Enforces type hints for inputs and outputs.
  - Default Values: Supports default values for optional parameters.
  - Autocompletion: Easier to work with in an Integrated Development Environment.
* Cons:
  - Inflexible: Adding/removing parameters requires modifying all function signatures.
  - Inconsistency: Different nodes may have different numbers of inputs/outputs, which prevents a
    uniform interface for the `execute` method.
  - Checkpoint Integration: Checkpoint storage and retrieval must be adapted to tuple-based outputs.
  - Loses Named Outputs: Returning a tuple makes it harder to identify what each value represents.


3. **Structured object (Dataclass or custom class)**
* Pros:
  - Structure: Each input/output follows a defined schema which is associated with the node, which
    prevents missing inputs and outputs. Robust specification of expected inputs and outputs and
    constraints (e.g. pydantic).
  - Type Safety: Schema validation ensures correct input types.
  - Readability: Named attributes clarify input/output semantics.
  - Access: Input values are accessible by the dot notation instead of dictionary keys.
  - Documentation: Clearly defines expected input/output fields in the custom object which stores
    inputs or outputs.
* Cons:
  - Additional code: Every node requires a unique dataclass. More complex to implement and maintain.
  - Serialization Complexity: Requires extra conversion steps to serialize/deserialize structured
    objects.


## Decision

**Chosen option**: 3. **Structured object (Dataclass or custom class)**

**Justification**:
- Option 2 is eliminated due to its inflexibility and inconsistency.
- Option 1 is eliminated due to:
  - Its lack of structure and type safety.
  - The need for manual validation and documentation of expected keys.
  - The overhead of key-based access and dictionary creation.
- Option 3 is chosen because:
  - It provides a structured and type-safe approach to defining inputs and outputs. It allows for
    integration with validation libraries like Pydantic.
  - It allows for central documentation of expected input/output fields within each custom object.
  - It aligns well with the concept of nodes as self-contained entities with well-defined
    interfaces.

## Future Implications

- Decide which structure object is the most appropriate. Consider integrating runtime validation
  (e.g., Pydantic) to enforce key presence and types while keeping a dictionary-based approach.
- Implement interaction with the IO handler to accept and provide data depending on the node which
  requests it.
- Introduce a conversion layer to make compatible with serialization.

### Suggestions to Improve the Implementation

Mitigate Boilerplate Overhead:
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

Serialization Strategy:
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


## Related Decisions
- [ADR-1]
