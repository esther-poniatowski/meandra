"""
meandra.cli_app
===============

Command-line interface for the meandra package.

Provides commands for:
- Running workflows from decorated pipeline classes
- Validating workflow configurations
- Inspecting workflow structure

Notes
-----
This module is the entry point for the ``meandra`` command-line tool,
powered by Typer.

Examples
--------
Run a pipeline:

    meandra run mymodule:MyPipeline --config config.yaml

Validate a configuration:

    meandra validate config.yaml --pipeline mymodule:MyPipeline

Show workflow info:

    meandra info

Functions
---------
cli_info
    Display version and platform diagnostics.
cli_run
    Run a workflow from a decorated pipeline class.
cli_validate
    Validate a configuration file.
cli_graph
    Display or export the workflow graph.
"""

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Type

import typer

from meandra import __version__, info


app = typer.Typer(
    name="meandra",
    add_completion=False,
    no_args_is_help=True,
    help="Workflow orchestration for data analysis pipelines.",
)


def _import_pipeline(module_path: str) -> Type[Any]:
    """
    Import a pipeline class from a module path.

    Parameters
    ----------
    module_path : str
        Module path in format 'module:ClassName' or 'module.submodule:ClassName'.

    Returns
    -------
    Type[Any]
        The imported pipeline class.

    Raises
    ------
    typer.BadParameter
        If the module path is invalid or the class cannot be imported.
    """
    if ":" not in module_path:
        raise typer.BadParameter(
            f"Invalid module path '{module_path}'. "
            "Expected format: 'module:ClassName' (e.g., 'mymodule:MyPipeline')"
        )

    module_name, class_name = module_path.rsplit(":", 1)

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise typer.BadParameter(f"Cannot import module '{module_name}': {e}")

    if not hasattr(module, class_name):
        raise typer.BadParameter(
            f"Module '{module_name}' has no attribute '{class_name}'"
        )

    return getattr(module, class_name)


def _load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from a file.

    Supports JSON and YAML formats.

    Parameters
    ----------
    config_path : Path
        Path to configuration file.

    Returns
    -------
    Dict[str, Any]
        Configuration dictionary.

    Raises
    ------
    typer.BadParameter
        If file cannot be read or parsed.
    """
    if not config_path.exists():
        raise typer.BadParameter(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()

    try:
        content = config_path.read_text()

        if suffix == ".json":
            return json.loads(content)
        elif suffix in (".yaml", ".yml"):
            try:
                import yaml

                return yaml.safe_load(content) or {}
            except ImportError:
                raise typer.BadParameter(
                    "YAML support requires PyYAML. Install with: pip install pyyaml"
                )
        else:
            # Try JSON first, then YAML
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                try:
                    import yaml

                    return yaml.safe_load(content) or {}
                except ImportError:
                    raise typer.BadParameter(
                        f"Unknown config format '{suffix}' and YAML not available"
                    )
    except Exception as e:
        raise typer.BadParameter(f"Failed to load config: {e}")


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@app.command("run")
def cli_run(
    pipeline: str = typer.Argument(
        ...,
        help="Pipeline to run in format 'module:ClassName'",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (JSON or YAML)",
        exists=False,  # We handle existence check ourselves
    ),
    param: Optional[list[str]] = typer.Option(
        None,
        "--param",
        "-p",
        help="Override parameter in format 'key=value' (can be repeated)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save workflow outputs (JSON)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Run a workflow from a decorated pipeline class.

    Parameters
    ----------
    pipeline : str
        Pipeline to run in format 'module:ClassName'.
    config : Optional[Path]
        Path to configuration file (JSON or YAML).
    param : Optional[list[str]]
        Override parameters in format 'key=value'.
    output : Optional[Path]
        Path to save workflow outputs (JSON).
    verbose : bool
        Enable verbose output.

    Examples
    --------
    ::

        meandra run mymodule:MyPipeline

        meandra run mymodule:MyPipeline --config config.yaml

        meandra run mymodule:MyPipeline -p data_path=/path/to/data
    """
    from meandra.api.decorators import get_pipeline_spec, build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError
    from meandra.orchestration.orchestrator import SchedulingOrchestrator

    # Import the pipeline class
    pipeline_cls = _import_pipeline(pipeline)

    # Validate it's a decorated pipeline
    spec = get_pipeline_spec(pipeline_cls)
    if spec is None:
        typer.echo(
            f"Error: {pipeline_cls.__name__} is not decorated with @pipeline",
            err=True,
        )
        raise typer.Exit(code=1)

    # Load configuration
    inputs: Dict[str, Any] = {}
    if config is not None:
        config_path = Path(config)
        inputs = _load_config(config_path)

    # Apply parameter overrides
    if param:
        for p in param:
            if "=" not in p:
                typer.echo(f"Error: Invalid parameter format '{p}'. Use 'key=value'", err=True)
                raise typer.Exit(code=1)
            key, value = p.split("=", 1)
            # Try to parse as JSON for complex values
            try:
                inputs[key] = json.loads(value)
            except json.JSONDecodeError:
                inputs[key] = value

    # Build workflow
    try:
        workflow = build_workflow(
            pipeline_cls,
            validate=True,
            available_inputs=set(inputs.keys()),
        )
    except (WorkflowValidationError, DependencyResolutionError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    if verbose:
        typer.echo(f"Running pipeline: {spec.name}")
        typer.echo(f"Nodes: {[n.name for n in workflow.nodes.values()]}")
        typer.echo(f"Inputs: {inputs}")

    # Execute workflow
    orchestrator = SchedulingOrchestrator()

    try:
        result = orchestrator.run(workflow, inputs)

        if verbose:
            typer.echo(f"Workflow completed successfully")

        # Save or display output
        if output:
            output.write_text(json.dumps(result, indent=2, default=str))
            typer.echo(f"Output saved to: {output}")
        else:
            typer.echo(json.dumps(result, indent=2, default=str))

    except Exception as e:
        typer.echo(f"Error: Workflow execution failed: {e}", err=True)
        if verbose:
            import traceback

            typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1)


@app.command("validate")
def cli_validate(
    config: Path = typer.Argument(
        ...,
        help="Path to configuration file to validate",
        exists=True,
    ),
    pipeline: Optional[str] = typer.Option(
        None,
        "--pipeline",
        "-p",
        help="Pipeline to validate against in format 'module:ClassName'",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Validate a configuration file.

    If --pipeline is provided, validates the config against the pipeline's
    expected inputs.

    Parameters
    ----------
    config : Path
        Path to configuration file to validate.
    pipeline : Optional[str]
        Pipeline to validate against in format 'module:ClassName'.
    verbose : bool
        Enable verbose output.

    Examples
    --------
    ::

        meandra validate config.yaml

        meandra validate config.yaml --pipeline mymodule:MyPipeline
    """
    from meandra.api.decorators import get_pipeline_spec, build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError

    # Load configuration
    config_data = _load_config(config)

    if verbose:
        typer.echo(f"Loaded configuration from: {config}")
        typer.echo(f"Keys: {list(config_data.keys())}")

    # Validate against pipeline if provided
    if pipeline:
        pipeline_cls = _import_pipeline(pipeline)

        spec = get_pipeline_spec(pipeline_cls)
        if spec is None:
            typer.echo(
                f"Error: {pipeline_cls.__name__} is not decorated with @pipeline",
                err=True,
            )
            raise typer.Exit(code=1)

        # Build workflow to get input requirements
        try:
            workflow = build_workflow(
                pipeline_cls,
                validate=True,
                available_inputs=set(config_data.keys()),
            )
        except (WorkflowValidationError, DependencyResolutionError, ValueError) as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1)

        # Collect all required inputs
        required_inputs = spec.required_inputs()

        # Check for missing inputs
        provided = set(config_data.keys())
        missing = required_inputs - provided

        if missing:
            typer.echo(f"Warning: Missing inputs: {sorted(missing)}", err=True)
        else:
            if verbose:
                typer.echo(f"All required inputs provided")

        # Check for extra keys
        extra = provided - required_inputs
        if extra and verbose:
            typer.echo(f"Extra keys in config: {sorted(extra)}")

    typer.echo(f"Configuration is valid: {config}")


@app.command("graph")
def cli_graph(
    pipeline: str = typer.Argument(
        ...,
        help="Pipeline to graph in format 'module:ClassName'",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save graph (PNG, SVG, or DOT format based on extension)",
    ),
) -> None:
    """
    Display or export the workflow graph.

    Shows nodes and their dependencies.

    Parameters
    ----------
    pipeline : str
        Pipeline to graph in format 'module:ClassName'.
    output : Optional[Path]
        Path to save graph (PNG, SVG, or DOT format based on extension).

    Examples
    --------
    ::

        meandra graph mymodule:MyPipeline

        meandra graph mymodule:MyPipeline --output workflow.dot
    """
    from meandra.api.decorators import get_pipeline_spec, build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError

    pipeline_cls = _import_pipeline(pipeline)

    spec = get_pipeline_spec(pipeline_cls)
    if spec is None:
        typer.echo(
            f"Error: {pipeline_cls.__name__} is not decorated with @pipeline",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        workflow = build_workflow(pipeline_cls, validate=True)
    except (WorkflowValidationError, DependencyResolutionError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    # Generate DOT representation
    lines = ["digraph workflow {", f'    label="{spec.name}"', "    rankdir=LR", ""]

    for node in workflow.nodes.values():
        # Node definition
        label = f"{node.name}"
        if node.inputs:
            label += f"\\nin: {', '.join(node.inputs)}"
        if node.outputs:
            label += f"\\nout: {', '.join(node.outputs)}"
        lines.append(f'    "{node.name}" [label="{label}", shape=box]')

    lines.append("")

    # Edges from dependencies
    for node in workflow.nodes.values():
        for dep in node.dependencies:
            lines.append(f'    "{dep}" -> "{node.name}"')

    lines.append("}")
    dot_content = "\n".join(lines)

    if output:
        suffix = output.suffix.lower()
        if suffix == ".dot":
            output.write_text(dot_content)
            typer.echo(f"DOT graph saved to: {output}")
        elif suffix in (".png", ".svg", ".pdf"):
            try:
                import subprocess

                proc = subprocess.run(
                    ["dot", f"-T{suffix[1:]}", "-o", str(output)],
                    input=dot_content,
                    text=True,
                    capture_output=True,
                )
                if proc.returncode != 0:
                    typer.echo(f"Error: graphviz failed: {proc.stderr}", err=True)
                    raise typer.Exit(code=1)
                typer.echo(f"Graph saved to: {output}")
            except FileNotFoundError:
                typer.echo(
                    "Error: graphviz not found. Install it or use .dot output format",
                    err=True,
                )
                raise typer.Exit(code=1)
        else:
            typer.echo(
                f"Error: Unknown output format '{suffix}'. "
                "Use .dot, .png, .svg, or .pdf",
                err=True,
            )
            raise typer.Exit(code=1)
    else:
        typer.echo(dot_content)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the package version and exit.",
    ),
) -> None:
    """
    Workflow orchestration for data analysis pipelines.

    Parameters
    ----------
    version : bool
        Show the package version and exit.
    """
    if version:
        typer.echo(f"meandra {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
