<a id="command-line-interface"></a>

# Command-Line Interface

Entry points for the `meandra` command-line tool.

<a id="module-meandra.cli_app"></a>

<a id="cli-application"></a>

## CLI Application

<a id="meandra-cli-app"></a>

### meandra.cli_app

Command-line interface for the meandra package.

Provides commands for:
- Running workflows from decorated pipeline classes
- Validating workflow configurations
- Inspecting workflow structure

### Notes

This module is the entry point for the `meandra` command-line tool,
powered by Typer.

### Examples

Run a pipeline:

> meandra run mymodule:MyPipeline –config config.yaml

Validate a configuration:

> meandra validate config.yaml –pipeline mymodule:MyPipeline

Show workflow info:

> meandra info

<a id="meandra.cli_app.cli_info"></a>

### meandra.cli_app.cli_info()

Display version and platform diagnostics.

<a id="meandra.cli_app.cli_run"></a>

### meandra.cli_app.cli_run(pipeline=<typer.models.ArgumentInfo object>, config=<typer.models.OptionInfo object>, param=<typer.models.OptionInfo object>, output=<typer.models.OptionInfo object>, verbose=<typer.models.OptionInfo object>)

Run a workflow from a decorated pipeline class.

* **Parameters:**
  * **pipeline** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Pipeline to run in format ‘module:ClassName’.
  * **config** (*Optional* *[**Path* *]*) – Path to configuration file (JSON or YAML).
  * **param** (*Optional* *[*[*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Override parameters in format ‘key=value’.
  * **output** (*Optional* *[**Path* *]*) – Path to save workflow outputs (JSON).
  * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Enable verbose output.

### Examples

```default
meandra run mymodule:MyPipeline

meandra run mymodule:MyPipeline --config config.yaml

meandra run mymodule:MyPipeline -p data_path=/path/to/data
```

<a id="meandra.cli_app.cli_validate"></a>

### meandra.cli_app.cli_validate(config=<typer.models.ArgumentInfo object>, pipeline=<typer.models.OptionInfo object>, verbose=<typer.models.OptionInfo object>)

Validate a configuration file.

If –pipeline is provided, validates the config against the pipeline’s
expected inputs.

* **Parameters:**
  * **config** (*Path*) – Path to configuration file to validate.
  * **pipeline** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Pipeline to validate against in format ‘module:ClassName’.
  * **verbose** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Enable verbose output.

### Examples

```default
meandra validate config.yaml

meandra validate config.yaml --pipeline mymodule:MyPipeline
```

<a id="meandra.cli_app.cli_graph"></a>

### meandra.cli_app.cli_graph(pipeline=<typer.models.ArgumentInfo object>, output=<typer.models.OptionInfo object>)

Display or export the workflow graph.

Shows nodes and their dependencies.

* **Parameters:**
  * **pipeline** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Pipeline to graph in format ‘module:ClassName’.
  * **output** (*Optional* *[**Path* *]*) – Path to save graph (PNG, SVG, or DOT format based on extension).

### Examples

```default
meandra graph mymodule:MyPipeline

meandra graph mymodule:MyPipeline --output workflow.dot
```

<a id="meandra.cli_app.main_callback"></a>

### meandra.cli_app.main_callback(version=<typer.models.OptionInfo object>)

Workflow orchestration for data analysis pipelines.

* **Parameters:**
  **version** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Show the package version and exit.
