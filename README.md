# Meandra

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/meandra)](https://github.com/esther-poniatowski/meandra/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Runs modular data processing pipelines with reproducible configurations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Complex data processing pipelines coordinate heterogeneous tasks across multi-stage
computations, often involving conditional branches, parameter sweeps, and intermediate
checkpoints. Existing workflow tools either impose rigid structures or lack flexibility
for non-linear, hierarchical workflows with precise parameter control.

### Advantages

- **Composable pipelines** — build reusable, hierarchical pipelines from atomic tasks.
- **Declarative configuration** — control parameters through structured files, runtime
  overrides, and hierarchical merging.
- **Dynamic I/O resolution** — automate file handling and path generation with dynamic
  rules and metadata tracking.
- **Execution orchestration** — resolve task dependencies, track progress, and manage
  failures and recovery.
- **Reproducible experiments** — rerun experiments with identical configurations and
  parameter sets.

---

## Features

### Configuration Management

- [ ] **Modular configuration**: Define structured, composable YAML configurations
  with optional JSON conversion.
- [ ] **Hierarchical merging**: Combine multiple configuration sources with
  customizable precedence.
- [ ] **Runtime overrides**: Modify parameters via command-line dot notation or
  alternate configuration files.
- [ ] **Variable interpolation**: Reference variables within configuration files to
  resolve parameters dynamically.
- [ ] **Dynamic path rules**: Specify input/output paths with runtime placeholders.

### Workflow Definition and Execution

- [ ] **Modular composition**: Define atomic computation nodes, reusable across
  workflows with nested loops and hierarchical pipelines.
- [ ] **Parameter sweeping**: Run multi-run experiments with complex parameter
  combinations.
- [ ] **Data catalog**: Automate data loading and saving with customizable path rules
  and format conversion.
- [ ] **Execution through aliases**: Launch workflows via aliases with custom parameter
  sets.
- [ ] **Execution tracking**: Display real-time task progress and status in the
  terminal.
- [ ] **Dependency resolution**: Schedule tasks automatically based on inter-step
  dependencies.
- [ ] **Parallel execution**: Run independent tasks concurrently.
- [ ] **Automated logging**: Configure logging for monitoring and debugging.
- [ ] **Outputs by run**: Generate output directories for distinct runs automatically.
- [ ] **Failure recovery**: Resume execution from the last successful step or
  checkpoint.
- [ ] **Reproducibility**: Rerun previous experiments with consistent configurations.

---

## Quick Start

Run a pipeline from a Python module:

```sh
meandra run my_module:MyPipeline --config config.yaml
```

Override parameters at runtime:

```sh
meandra run my_module:MyPipeline -p learning_rate=0.01 -p epochs=50
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Defining nodes, assembling pipelines, CLI, Python API |
| [Concepts](docs/guide/concepts.md) | Core abstractions and design |
| [Tutorials](docs/guide/tutorials.md) | Step-by-step walkthroughs |
| [Architecture](docs/architecture/) | Design overview and patterns |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/meandra](https://esther-poniatowski.github.io/meandra/).

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
