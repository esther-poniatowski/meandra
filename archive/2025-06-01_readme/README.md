# Meandra

Meandra is a workflow automation framework that defines and executes modular, scalable, and
reproducible data pipelines. It integrates hierarchical configuration, task-oriented orchestration,
execution tracking and I/O management to streamline complex data workflows.

## Motivation

Existing tools for configuration management and workflow automation often impose rigid structures or
lack flexibility for complex, non linear data workflows.

Meandra addresses these challenges by providing:

- Modular, task-oriented workflows definition.
- Flexible configuration and execution management.
- Automated input loading and output saving with metadata recording.

These features make Meandra particularly suitable for scientific data analysis projects.

## Features

### Configuration Management

- **YAML-based Configuration**: Define structured and nested parameters in YAML files, with optional
  JSON conversion.
- **Variable Interpolation**: Reference variables within configuration files for dynamic parameter
  setting.
- **Required Parameters**: Enforce mandatory runtime parameters to ensure all necessary inputs are
  provided.
- **Modular Configurations**: Organize reusable and composable configuration files for improved
  clarity and maintainability.
- **Hierarchical Merging**: Combine multiple configuration sources with customizable precedence.
- **Runtime Overrides**: Modify parameters via command-line inputs using dot notation, or alternate
  configuration files.
- **Centralized Parameter Access**: Retrieve parameters from a unified configuration object using
  dot notation.
- **Optional Schema Validation**: Optionally validate parameters using type hints and constraints
  for data integrity.
- **Dynamic Path Rules**: Specify flexible input/output paths with runtime placeholders for complex
  file management.
- **Flexible Data Catalog**: Automate data loading and saving with with customizable rules.

### workflow Definition and Execution

- **Modular Composition**: Define atomic computation units (nodes) that can be shared across
  workflows, and composed into sub-workflows for nested loops and complex workflows.
- **Dependency Resolution**: Automatically schedule tasks based on inter-step dependencies within
  workflows.
- **Custom Entry Points**: Launch workflows from the command line for dynamic instantiation.
- **Parallel Execution**: Run independent tasks concurrently for improved performance.
- **Automated Logging**: Customize logging options for comprehensive monitoring and debugging.
- **Execution Tracking**: Display real-time task progress and status in the terminal.
- **Parameter Sweeping**: Conduct multi-run experiments with complex parameter combinations.
- **Run-based Outputs**: Automatically generate output directories for different runs.
- **Failure Handling & Recovery**: Implement robust error management and checkpointing to resume
  execution from the last successful step or an intermediate checkpoint.
- **Reproducibility**: Rerun previous experiments with consistent configurations.

## Installation

Meandra is currently available for installation directly from its GitHub repository.

To install the package and its dependencies in an activated virtual environment:

```bash
pip install git+https://github.com/esther-poniatowski/meandra.git
```

To install a specific version, specify the version tag in the URL:

```bash
pip install git+https://github.com/esther-poniatowski/meandra.git@v0.1.0
```

## Quick Start

1. Define configurations in `config.yaml`:

    ```yaml
    # TODO: Add examples
    ```

2. Create modular nodes for atomic computations.

    ```python
    # TODO: Add examples
    ```

3. Build workflows by specifying task dependencies.


    ```python
    # TODO: Add examples
    ```

4. Execute the workflow using the custom entry point:

    ```bash
    python run_workflow.py --workflow-name my_workflow
    ```

## Documentation

For detailed documentation, visit [Documentation Link](#).

## License

This project is licensed under the [GNU license](LICENSE).
