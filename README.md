# meandra

Flexible Python framework for modular data workflows with structured configurations.

Meandra is a Python library designed to streamline data analysis workflows, integrating configuration management, pipeline orchestration and execution tracking. It offers a lightweight, flexible, and customizable approach to define and run complex data analysis pipelines in a modular way.

## Features

### Configuration Management

- **YAML-based Configuration**: Define structured and nested parameters in YAML files, with JSON conversion support.
- **Variable Interpolation**: Reference variables within configuration files.
- **Required Parameters**: Specify mandatory runtime parameters.
- **Modular Configurations**: Separate concerns with reusable configuration files.
- **Hierarchical Merging**: Combine multiple configuration sources with customizable precedence.
- **Runtime Overrides**: Modify parameters via command-line inputs using dot notation, or alternate configuration files.
- **Centralized Parameter Access**: Use dot notation to access a unified configuration object.
- **Optional Schema Validation**: Validate parameters with type hints and constraints.
- **Dynamic Path Rules**: Specify complex input/output paths with runtime placeholders.
- **Flexible Data Catalog**: Automate data loading and saving with with customizable rules.


### Pipeline Definition

- **Reusable Nodes**: Define modular computation units shareable across pipelines.
- **Dependency Resolution**: Schedule tasks based on inter-step dependencies within pipelines.
- **Custom Entry Points**: Run pipelines from the command line with dynamic class instantiation.
- **Parallel Execution**: Run independent tasks concurrently.
- **Automated Logging**: Customize logging options for comprehensive tracking.
- **Execution Tracking**: Monitor task status and progress in the console.
- **Parameter Sweeping**: Conduct multi-run experiments with complex parameter matrices.
- **Run-based Outputs**: Automatically create and manage output directories for each run.
- **Failure Handling**: Implement robust error management and recovery mechanisms.
- **Checkpointing**: Resume execution from intermediate points or the last successful step.
- **Reproducibility**: Rerun previous experiments with similar configurations.


## Motivation

Existing tools for configuration management and workflow automation often impose rigid structures or lack flexibility for scientific workflows. This library is tailored to scientific data analysis challenges, offering:
- Lightweight project overhead.
- Highly adaptable configuration and data management.
- Flexible, task-oriented pipeline design and execution.

## Installation

```bash
pip install scientific-pipeline
```

## Quick Start

1. Define configurations in `config.yaml`:

```yaml
pipeline:
  name: example_pipeline
  steps:
    - load_data
    - preprocess
    - analyze
    - visualize

data:
  input_path: ${data.base_path}/input
  output_path: ${data.base_path}/output
  base_path: /path/to/data

parameters:
  analysis:
    method: pca
    n_components: 3
```

2. Create modular nodes for atomic computations.
  
3. Build pipelines by specifying task dependencies.

```python
from sciflow import Pipeline, task

class ExamplePipeline(Pipeline):
    @task
    def load_data(self):
        # Implementation

    @task
    def preprocess(self):
        # Implementation

    @task
    def analyze(self):
        # Implementation

    @task
    def visualize(self):
        # Implementation
```

4. Execute the pipeline using the custom entry point:

 ```bash
 python run_pipeline.py --pipeline-name my_pipeline
 ```

## Documentation

For detailed documentation, visit [Documentation Link](#).


## License
This project is licensed under the GNU License. See the [LICENSE](LICENSE) file for details.

