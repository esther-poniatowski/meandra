# Architectural Overview

Meandra is a modular workflow system that separates definition, execution, and infrastructure
concerns.

## Core Components

### Node

The `Node` class represents a single unit of computation:

- Wraps a callable function
- Declares input/output keys
- Specifies dependencies on other nodes
- Optionally supports checkpointing

### Workflow

The `Workflow` class represents a directed acyclic graph (DAG):

- Contains a collection of nodes
- Validates node dependencies
- Provides traversal and query operations

### Orchestrator

The `Orchestrator` interface defines workflow execution:

- `SchedulingOrchestrator`: Resolves dependencies and executes nodes in topological order
- Manages state through `StateTracker`
- Handles errors and checkpointing

## Layered Architecture

### Layer 1: User-Facing API

Provides two approaches for workflow definition:

1. **Decorator API**: `@pipeline` and `@node` decorators
2. **Fluent API**: `step()` and `pipe()` builders

Both APIs produce the same `Workflow` objects.

### Layer 2: Orchestration

Handles workflow execution:

- **Scheduler**: Resolves node dependencies using topological sort
- **Orchestrator**: Executes nodes in order, managing state
- **StateTracker**: Tracks execution state and results

### Layer 3: Core

Provides fundamental abstractions:

- `Node`: Computation unit
- `Workflow`: Node collection with DAG structure
- Error types: `MeandraError` hierarchy

### Layer 4: Infrastructure

Provides supporting services:

- **DataCatalog**: Dataset registration and I/O
- **CheckpointManager**: Persistence and recovery
- **ProgressTracker**: Execution monitoring
- **Logging**: Structured logging with context

## Data Flow

```
User Input --> Workflow Definition --> Workflow --> Orchestrator
                    |                              |
                    |                              v
                    |                         Scheduler
                    |                              |
                    |                              v
                    └───────────────────> Node Execution
                                                   |
                                                   v
                                              State Updates
                                                   |
                                                   v
                                              Checkpoints
                                                   |
                                                   v
                                               Results
```
