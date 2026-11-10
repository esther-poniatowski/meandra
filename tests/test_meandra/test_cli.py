"""
Tests of the command-line interface against the command-line conventions.

Each test runs the Typer application in process, on a pipeline module written
to a temporary folder.
"""

import json
import sys
import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from meandra import __version__
from meandra.cli_app import app

PIPELINE_SOURCE = textwrap.dedent(
    '''
    from meandra.api import node, pipeline


    @pipeline(name="scale")
    class Scale:
        @node(inputs=["value", "factor"], outputs=["scaled"])
        def scale(self, inputs):
            return {"scaled": inputs["value"] * inputs["factor"]}


    class Plain:
        pass
    '''
)


@pytest.fixture
def runner() -> CliRunner:
    """Return a runner of the application."""
    return CliRunner()


@pytest.fixture
def pipeline_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Write an importable pipeline module and return its name."""
    name = f"cli_pipeline_{tmp_path.name.replace('-', '_')}"
    (tmp_path / f"{name}.py").write_text(PIPELINE_SOURCE)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.chdir(tmp_path)
    yield name
    sys.modules.pop(name, None)


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version_flags_print_the_version(runner: CliRunner, flag: str) -> None:
    result = runner.invoke(app, [flag])
    assert result.exit_code == 0
    assert result.output.strip() == f"meandra {__version__}"


@pytest.mark.parametrize(
    "args",
    [
        ["-V"],
        ["run", "x:Y", "--config", "inputs.json"],
        ["run", "x:Y", "-c", "inputs.json"],
        ["run", "x:Y", "-v"],
        ["validate", "inputs.json", "-v"],
    ],
)
def test_retired_names_are_usage_errors(runner: CliRunner, args: list[str]) -> None:
    assert runner.invoke(app, args).exit_code == 2


def test_run_reads_the_inputs_file(runner: CliRunner, pipeline_module: str) -> None:
    Path("inputs.json").write_text(json.dumps({"value": 3}))
    result = runner.invoke(
        app,
        ["run", f"{pipeline_module}:Scale", "-i", "inputs.json", "-p", "factor=2", "-o", "out.json"],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(Path("out.json").read_text())["scaled"] == 6


def test_run_exit_statuses(runner: CliRunner, pipeline_module: str) -> None:
    malformed = runner.invoke(app, ["run", f"{pipeline_module}:Scale", "-p", "factor"])
    assert malformed.exit_code == 2
    undecorated = runner.invoke(app, ["run", f"{pipeline_module}:Plain"])
    assert undecorated.exit_code == 2
    missing_file = runner.invoke(app, ["run", f"{pipeline_module}:Scale", "-i", "absent.json"])
    assert missing_file.exit_code == 2
    unsatisfied = runner.invoke(app, ["run", f"{pipeline_module}:Scale", "-p", "value=1"])
    assert unsatisfied.exit_code == 1


def test_validate_exit_statuses(runner: CliRunner, pipeline_module: str) -> None:
    Path("complete.json").write_text(json.dumps({"value": 1, "factor": 2}))
    Path("partial.json").write_text(json.dumps({"value": 1}))
    complete = runner.invoke(app, ["validate", "complete.json", "--pipeline", f"{pipeline_module}:Scale"])
    assert complete.exit_code == 0, complete.output
    partial = runner.invoke(app, ["validate", "partial.json", "--pipeline", f"{pipeline_module}:Scale"])
    assert partial.exit_code == 1


def test_graph_rejects_an_unknown_output_format(runner: CliRunner, pipeline_module: str) -> None:
    result = runner.invoke(app, ["graph", f"{pipeline_module}:Scale", "-o", "graph.txt"])
    assert result.exit_code == 2
    assert not Path("graph.txt").exists()
