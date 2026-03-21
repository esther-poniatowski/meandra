# Architecture

This section describes the design decisions and architectural patterns in Meandra.

```{toctree}
:maxdepth: 2

overview
patterns
```

## Overview

Meandra follows a layered architecture:

```
┌─────────────────────────────────────────────┐
│                 User-Facing API             │
│          (@pipeline, @node, step, pipe)     │
├─────────────────────────────────────────────┤
│              Orchestration Layer            │
│     (SchedulingOrchestrator, Scheduler)     │
├─────────────────────────────────────────────┤
│                  Core Layer                 │
│           (Node, Workflow, Errors)          │
├─────────────────────────────────────────────┤
│               Infrastructure                │
│   (DataCatalog, Checkpoint, Logging)        │
└─────────────────────────────────────────────┘
```

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Inversion**: High-level modules don't depend on low-level details
3. **Open/Closed**: Extensible through inheritance and composition
4. **Explicit Dependencies**: Node dependencies are declared, not inferred

## Module Dependencies

```
api ─────────────────┐
                     │
orchestration ───────┼──► core
                     │
datastore ───────────┘
     │
     └──► monitoring
```
