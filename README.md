# Meandra

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/meandra)](https://github.com/esther-poniatowski/meandra/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Runs modular data processing pipelines with reproducible configurations.

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

Complex data processing pipelines coordinate heterogeneous tasks across multi-stage computations,
often involving conditional branches, parameter sweeps, and intermediate checkpoints.

Existing workflow tools either impose rigid structures or lack flexibility for non-linear,
hierarchical workflows with precise parameter control. Reproducing results, logging runs,
and adapting to runtime changes typically require substantial boilerplate.

### Advantages

Meandra defines and executes modular, scalable, and reproducible workflows:

- **Composable pipelines**: Build reusable, hierarchical pipelines from atomic tasks.
- **Declarative configuration**: Control parameters through structured files, runtime overrides,
  and hierarchical merging.
- **Dynamic I/O resolution**: Automate file handling and path generation with dynamic rules and
  metadata tracking.
- **Execution orchestration**: Resolve task dependencies, track progress, and manage failures
  and recovery.
- **Reproducible experiments**: Rerun experiments with identical configurations and parameter sets.

These features make Meandra suited for scientific data analysis and simulation research.

---

## Features

### Configuration Management

- [ ] **Modular configuration**: Define structured, composable configuration files in YAML with
  optional JSON conversion.
- [ ] **Hierarchical merging**: Combine multiple configuration sources with customizable precedence.
- [ ] **Runtime overrides**: Modify parameters via command-line dot notation or alternate
  configuration files.
- [ ] **Variable interpolation**: Reference variables within configuration files to resolve
  parameters dynamically.
- [ ] **Dynamic path rules**: Specify input/output paths with runtime placeholders.

### Workflow Definition and Execution

- [ ] **Modular composition**: Define atomic computation nodes, reusable across workflows with
  multiple levels for nested loops and hierarchical pipelines.
- [ ] **Parameter sweeping**: Run multi-run experiments with complex parameter combinations.
- [ ] **Data catalog**: Automate data loading and saving with customizable path rules and format
  conversion.
- [ ] **Execution through aliases**: Launch workflows via aliases with custom parameter sets.
- [ ] **Execution tracking**: Display real-time task progress and status in the terminal.
- [ ] **Dependency resolution**: Schedule tasks automatically based on inter-step dependencies.
- [ ] **Parallel execution**: Run independent tasks concurrently.
- [ ] **Automated logging**: Configure logging for monitoring and debugging.
- [ ] **Outputs by run**: Generate output directories for distinct runs automatically.
- [ ] **Failure recovery**: Resume execution from the last successful step or checkpoint.
- [ ] **Reproducibility**: Rerun previous experiments with consistent configurations.

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/meandra.git
```

### Using conda

Install from the eresthanaconda channel:

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

Run a pipeline defined in a Python module:

```sh
meandra run my_module:MyPipeline --config config.yaml
```

Override parameters at runtime:

```sh
meandra run my_module:MyPipeline -p learning_rate=0.01 -p epochs=50
```

Validate a configuration file against a pipeline:

```sh
meandra validate config.yaml --pipeline my_module:MyPipeline
```

Export the workflow graph as an image:

```sh
meandra graph my_module:MyPipeline --output workflow.png
```

### Programmatic Usage

Define a pipeline with decorators:

```python
from meandra.api.decorators import pipeline, node
from meandra.orchestration.orchestrator import SchedulingOrchestrator
from meandra.api.build import build_workflow

@pipeline(name="data_processing")
class DataPipeline:
    @node(outputs=["raw_data"])
    def load(self, inputs):
        return {"raw_data": load_from_disk()}

    @node(inputs=["raw_data"], outputs=["result"], depends_on=["load"])
    def process(self, inputs):
        return {"result": transform(inputs["raw_data"])}

# Build and run the workflow
workflow = build_workflow(DataPipeline, validate=True)
orchestrator = SchedulingOrchestrator()
results = orchestrator.run(workflow, {})
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
