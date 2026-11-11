"""
meandra.cli_app
===============

Command-line interface for the meandra package.

Provides commands for:
- Running workflows from decorated pipeline classes
- Validating the inputs file of a run
- Inspecting workflow structure

Notes
-----
This module is the entry point for the ``meandra`` command-line tool,
powered by Typer. The options follow the command-line conventions of the
workspace. Meandra has no configuration file and works on no project root: the
inputs file of a run is a run input, named by ``--inputs``, since the
conventions reserve ``--config`` for the configuration file of a tool.

The exit status is 0 on success, 1 when a validation or a run finds a
problem, and 2 on a usage error.

Examples
--------
Run a pipeline:

    meandra run mymodule:MyPipeline --inputs inputs.yaml

Validate an inputs file:

    meandra validate inputs.yaml --pipeline mymodule:MyPipeline

Show workflow info:

    meandra info
"""

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Type

import typer

from meandra import __version__, info


EXIT_PROBLEM = 1
"""Exit status of a validation or a run that finds a problem."""

EXIT_USAGE = 2
"""Exit status of a usage error, such as a malformed option value."""


def _usage_error(message: str) -> typer.Exit:
    """
    Print a usage error and return the exit that carries its status.

    Parameters
    ----------
    message : str
        Description of the error.

    Returns
    -------
    typer.Exit
        Exit with status `EXIT_USAGE`, to be raised by the caller.
    """
    typer.echo(f"Error: {message}", err=True)
    return typer.Exit(code=EXIT_USAGE)


def _require_pipeline_spec(pipeline_cls: Type[Any]) -> Any:
    """
    Return the specification of a decorated pipeline class.

    Parameters
    ----------
    pipeline_cls : Type[Any]
        Class named on the command line.

    Returns
    -------
    PipelineSpec
        Specification attached by the ``@pipeline`` decorator.

    Raises
    ------
    typer.Exit
        With status `EXIT_USAGE` when the class is not decorated.
    """
    from meandra.api.decorators import get_pipeline_spec

    spec = get_pipeline_spec(pipeline_cls)
    if spec is None:
        raise _usage_error(f"{pipeline_cls.__name__} is not decorated with @pipeline")
    return spec


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


def _load_inputs(config_path: Path) -> Dict[str, Any]:
    """
    Load the inputs of a run from a file.

    Supports JSON and YAML formats.

    Parameters
    ----------
    config_path : Path
        Path to the inputs file, relative to the current folder.

    Returns
    -------
    Dict[str, Any]
        Inputs dictionary.

    Raises
    ------
    typer.BadParameter
        If file cannot be read or parsed.
    """
    if not config_path.exists():
        raise typer.BadParameter(f"Inputs file not found: {config_path}")

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
                        f"Unknown inputs format '{suffix}' and YAML not available"
                    )
    except Exception as e:
        raise typer.BadParameter(f"Failed to load inputs: {e}")


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
    inputs_file: Optional[Path] = typer.Option(
        None,
        "--inputs",
        "-i",
        help="Path to the inputs file of the run (JSON or YAML)",
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
        help="Enable verbose output",
    ),
) -> None:
    """
    Run a workflow from a decorated pipeline class.

    Parameters
    ----------
    pipeline : str
        Pipeline to run in format 'module:ClassName'.
    inputs_file : Optional[Path]
        Path to the inputs file of the run (JSON or YAML).
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

        meandra run mymodule:MyPipeline --inputs inputs.yaml

        meandra run mymodule:MyPipeline -p data_path=/path/to/data
    """
    from meandra.api.decorators import build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError
    from meandra.orchestration.orchestrator import SchedulingOrchestrator

    # Import the pipeline class
    pipeline_cls = _import_pipeline(pipeline)
    spec = _require_pipeline_spec(pipeline_cls)

    # Load the inputs file
    inputs: Dict[str, Any] = {}
    if inputs_file is not None:
        inputs = _load_inputs(Path(inputs_file))

    # Apply parameter overrides
    if param:
        for p in param:
            if "=" not in p:
                raise _usage_error(f"Invalid parameter format '{p}'. Use 'key=value'")
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
        raise typer.Exit(code=EXIT_PROBLEM)

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
        raise typer.Exit(code=EXIT_PROBLEM)


@app.command("validate")
def cli_validate(
    inputs_file: Path = typer.Argument(
        ...,
        metavar="INPUTS",
        help="Path to the inputs file to validate",
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
        help="Enable verbose output",
    ),
) -> None:
    """
    Validate an inputs file.

    If --pipeline is provided, validates the inputs against the pipeline's
    expected inputs, and exits with status 1 when one is missing.

    Parameters
    ----------
    inputs_file : Path
        Path to the inputs file to validate.
    pipeline : Optional[str]
        Pipeline to validate against in format 'module:ClassName'.
    verbose : bool
        Enable verbose output.

    Examples
    --------
    ::

        meandra validate inputs.yaml

        meandra validate inputs.yaml --pipeline mymodule:MyPipeline
    """
    from meandra.api.decorators import build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError

    # Load the inputs file
    config_data = _load_inputs(inputs_file)

    if verbose:
        typer.echo(f"Loaded inputs from: {inputs_file}")
        typer.echo(f"Keys: {list(config_data.keys())}")

    # Validate against pipeline if provided
    if pipeline:
        pipeline_cls = _import_pipeline(pipeline)
        spec = _require_pipeline_spec(pipeline_cls)

        # Build workflow to get input requirements
        try:
            workflow = build_workflow(
                pipeline_cls,
                validate=True,
                available_inputs=set(config_data.keys()),
            )
        except (WorkflowValidationError, DependencyResolutionError, ValueError) as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=EXIT_PROBLEM)

        # Collect all required inputs
        required_inputs = spec.required_inputs()

        # Check for missing inputs
        provided = set(config_data.keys())
        missing = required_inputs - provided

        if missing:
            typer.echo(f"Error: Missing inputs: {sorted(missing)}", err=True)
            raise typer.Exit(code=EXIT_PROBLEM)
        if verbose:
            typer.echo("All required inputs provided")

        # Check for extra keys
        extra = provided - required_inputs
        if extra and verbose:
            typer.echo(f"Extra keys in the inputs file: {sorted(extra)}")

    typer.echo(f"Inputs file is valid: {inputs_file}")


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
    from meandra.api.decorators import build_workflow
    from meandra.core.errors import ValidationError as WorkflowValidationError, DependencyResolutionError

    pipeline_cls = _import_pipeline(pipeline)
    spec = _require_pipeline_spec(pipeline_cls)

    try:
        workflow = build_workflow(pipeline_cls, validate=True)
    except (WorkflowValidationError, DependencyResolutionError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=EXIT_PROBLEM)

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
                    raise typer.Exit(code=EXIT_PROBLEM)
                typer.echo(f"Graph saved to: {output}")
            except FileNotFoundError:
                typer.echo(
                    "Error: graphviz not found. Install it or use .dot output format",
                    err=True,
                )
                raise typer.Exit(code=EXIT_PROBLEM)
        else:
            raise _usage_error(
                f"Unknown output format '{suffix}'. Use .dot, .png, .svg, or .pdf"
            )
    else:
        typer.echo(dot_content)


def _print_version(value: bool) -> None:
    """
    Print the version and exit, before Click requires a command.

    Parameters
    ----------
    value : bool
        Whether the option ``--version`` was given.

    Raises
    ------
    typer.Exit
        With status 0 after printing the version.
    """
    if value:
        typer.echo(f"meandra {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        is_eager=True,
        callback=_print_version,
        help="Show the package version and exit.",
    ),
) -> None:
    """
    Workflow orchestration for data analysis pipelines.

    Parameters
    ----------
    version : bool
        Show the package version and exit; handled by `_print_version`.
    """


if __name__ == "__main__":
    app()
