# Meandra

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2025)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Workflow manager for building modular processing pipelines with structured configuration and flexible task orchestration.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Complex data processing pipelines often require the coordination of heterogeneous tasks, structured
configurations, and multi-stage computations. These workflows frequently involve conditional
execution paths, parameter sweeps, custom input/output formats, and intermediate checkpointing.

Existing tools for configuration management and workflow automation either impose rigid and
monolithic structures, or lack the flexibility to express non-linear or hierarchical workflows with
fine-grained parameter control. Moreover, managing reproducibility, logging, and runtime variability
typically requires substantial boilerplate or external tooling.

### Advantages

Meandra introduces a workflow automation framework for defining and executing modular, scalable, and
reproducible workflows.

It provides the following benefits:

- **Modular workflow composition**: Design reusable and hierarchical pipelines from atomic tasks.
- **Declarative configuration management**: Control parameters through structured configuration files, runtime overrides, and hierarchical merging.
- **Flexible input/output resolution**: Automate file handling and path generation with dynamic rules and metadata tracking.
- **Execution orchestration and monitoring**: Resolve task dependencies, track progress, manage
  failures and recovery.
- **Reproducible experimentation**: Rerun experiments with identical configurations, parameter sets,
  and outputs.

These features make Meandra particularly suited for scientific data analysis and experimental
simulation research.

---

## Features

### Configuration Management

- [ ] **Modular Configuration**: Define structured and nested parameters in reusable and composable configuration files in YAML format, with optional
  JSON conversion.
- [ ] **Hierarchical Merging**: Combine multiple configuration sources with customizable precedence.
- [ ] **Runtime Overrides**: Modify parameters via command-line inputs using dot notation, or alternate
  configuration files.
- [ ] **Variable Interpolation**: Reference variables within configuration files for dynamic parameter
  setting.
- [ ] **Dynamic Path Rules**: Specify flexible input/output paths with runtime placeholders for complex
  file management.

### Workflow Definition and Execution

- [ ] **Modular Composition**: Define atomic computation units (nodes) that can be reused and
  combined across multi-level workflows for nested loops and hierarchical pipelines.
- [ ] **Parameter Sweeping**: Conduct multi-run experiments with complex parameter combinations.
- [ ] **Data Catalog**: Automate data loading and saving with customizable path rules and format
  conversion.
- [ ] **Direct Execution**: Launch workflows with aliases for dynamic instantiation with custom
  parameter sets.
- [ ] **Execution Tracking**: Display real-time task progress and status in the terminal.
- [ ] **Node Dependency Resolution**: Automatically schedule tasks based on inter-step dependencies
  within workflows.
- [ ] **Parallel Execution**: Run independent tasks concurrently for improved performance.
- [ ] **Automated Logging**: Select logging options for comprehensive monitoring and debugging.
- [ ] **Run-based Outputs**: Automatically generate output directories for distinct runs.
- [ ] **Failure Handling & Recovery**: Implement robust error management and checkpointing to resume
  execution from the last successful step or an intermediate checkpoint.
- [ ] **Reproducibility**: Rerun previous experiments with consistent configurations.

---

## Installation

To install the package and its dependencies, use one of the following methods:

### Using Pip Installs Packages

Install the package from the GitHub repository URL via `pip`:

```bash
pip install git+https://github.com/esther-poniatowski/meandra.git
```

### Using Conda

Install the package from the private channel eresthanaconda:

```bash
conda install meandra -c eresthanaconda
```

### From Source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/meandra.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd meandra
      conda env create -f environment.yml
      ```

---

## Usage

### Command Line Interface (CLI)

To display the list of available commands and options:

```sh
meandra --help
```

### Programmatic Usage

To use the package programmatically in Python:

```python
import meandra
```

---

## Configuration

### Environment Variables

|Variable|Description|Default|Required|
|---|---|---|---|
|`VAR_1`|Description 1|None|Yes|
|`VAR_2`|Description 2|`false`|No|

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

```yaml
var_1: value1
var_2: value2
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/meandra/guide/)
- [API Documentation](https://esther-poniatowski.github.io/meandra/api/)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/meandra/issues)

**Email**: `{{ contact@example.com }}`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `{{ contact@example.com }}`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[Library A](link)** - Purpose
- **[Library B](link)** - Purpose

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
