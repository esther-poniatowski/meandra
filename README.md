# meandra


Meandra is a Python library designed to streamline modular data workflows, integrating structured
configuration management, pipeline orchestration, and execution tracking. It provides a lightweight,
flexible, and customizable approach to defining and executing complex data processing pipelines.


## Key Features

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


### Pipeline Definition and Execution

- **Modular Composition**: Define atomic computation units (nodes) that can be shared across
  pipelines, and composed into sub-pipelines for nested loops and complex workflows.
- **Dependency Resolution**: Automatically schedule tasks based on inter-step dependencies within
  pipelines.
- **Custom Entry Points**: Launch pipelines from the command line for dynamic instantiation.
- **Parallel Execution**: Run independent tasks concurrently for improved performance.
- **Automated Logging**: Customize logging options for comprehensive monitoring and debugging.
- **Execution Tracking**: Display real-time task progress and status in the terminal.
- **Parameter Sweeping**: Conduct multi-run experiments with complex parameter combinations.
- **Run-based Outputs**: Automatically generate output directories for different runs.
- **Failure Handling & Recovery**: Implement robust error management and checkpointing to resume
  execution from the last successful step or an intermediate checkpoint.
- **Reproducibility**: Rerun previous experiments with consistent configurations.


## Motivation

Existing tools for configuration management and workflow automation often impose rigid structures or
lack flexibility for complex, non linear data workflows.

Meandra is designed to address these challenges by providing:
- Highly adaptable configuration and data management.
- Modular, task-oriented approach to pipeline definition and execution.
- Minimal project overhead.

These features make Meandra particularly suitable for scientific data analysis projects.

## Installation

```bash
pip install scientific-pipeline
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

3. Build pipelines by specifying task dependencies.


```python
# TODO: Add examples
```

4. Execute the pipeline using the custom entry point:

 ```bash
 python run_pipeline.py --pipeline-name my_pipeline
 ```

## Documentation

For detailed documentation, visit [Documentation Link](#).


## License

This project is licensed under the GNU License. See the [LICENSE](LICENSE) file for details.
