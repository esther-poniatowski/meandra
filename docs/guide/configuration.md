# Configuration

Meandra accepts pipeline inputs as JSON or YAML files, passed via `--config`
on the CLI or loaded directly in Python. Parameter overrides merge on top of
file-based configuration.

## File Formats

### YAML

```yaml
data_path: /data/experiment_01
learning_rate: 0.001
epochs: 100
batch_size: 32
output_dir: /results/run_01
```

### JSON

```json
{
  "data_path": "/data/experiment_01",
  "learning_rate": 0.001,
  "epochs": 100,
  "batch_size": 32,
  "output_dir": "/results/run_01"
}
```

Both formats produce a flat dictionary of key-value pairs. Nested structures
are supported and passed through as-is.

YAML requires `pyyaml` (`pip install pyyaml`). JSON has no extra dependencies.

## Loading on the CLI

Pass a configuration file with `--config` / `-c`:

```sh
meandra run mymodule:MyPipeline --config config.yaml
```

Override or add individual parameters with `--param` / `-p`:

```sh
meandra run mymodule:MyPipeline -c config.yaml -p learning_rate=0.0001 -p epochs=200
```

Parameter overrides take precedence over file values. The CLI parses override
values as JSON when possible (numbers, booleans, arrays, objects). Unparseable
values are treated as strings.

## Loading in Python

Load a config dict and pass directly to the orchestrator:

```python
import yaml
from pathlib import Path
from meandra import SchedulingOrchestrator
from meandra.api import build_workflow

config = yaml.safe_load(Path("config.yaml").read_text())
workflow = build_workflow(MyPipeline, validate=True, available_inputs=set(config.keys()))
orchestrator = SchedulingOrchestrator()
result = orchestrator.run(workflow, config)
```

## ConfigProvider Protocol

For richer configuration systems (Hydra, OmegaConf, Tessara), implement the
`ConfigProvider` protocol:

```python
from meandra.configuration import ConfigProvider

class MyConfigProvider:
    def __init__(self, data: dict):
        self._data = data

    def get(self, path: str):
        """Retrieve a value by dotted path (e.g. 'model.lr')."""
        keys = path.split(".")
        value = self._data
        for key in keys:
            value = value[key]
        return value

    def to_dict(self) -> dict:
        """Return a resolved dictionary representation."""
        return dict(self._data)

    def resolve(self) -> None:
        """Resolve interpolations or dynamic values."""
        pass

    def snapshot(self, path: str) -> None:
        """Persist a configuration snapshot to disk."""
        import json
        Path(path).write_text(json.dumps(self._data, indent=2))
```

`SchedulingOrchestrator.run()` accepts a `ConfigProvider` directly in place of
a dict. The orchestrator calls `resolve()` then `to_dict()` before execution.

```python
provider = MyConfigProvider({"data_path": "/data", "lr": 0.01})
result = orchestrator.run(workflow, provider)
```

## Validation

Validate a configuration file against a pipeline before execution:

```sh
meandra validate config.yaml --pipeline mymodule:MyPipeline
```

The `validate` command:

1. Parses the file (JSON or YAML).
2. Builds the pipeline workflow graph.
3. Compares configuration keys against required inputs.
4. Reports missing keys as warnings.

Programmatic validation:

```python
workflow = build_workflow(MyPipeline, validate=True, available_inputs=set(config.keys()))
result = workflow.validate(available_inputs=set(config.keys()))
if not result.valid:
    print(result.errors)
```

## Parameter Override Semantics

Override values passed with `--param` / `-p` follow these rules:

| Input | Parsed As |
|---|---|
| `42` | `int` |
| `0.001` | `float` |
| `true` / `false` | `bool` |
| `[1, 2, 3]` | `list` |
| `{"key": "val"}` | `dict` |
| `hello` | `str` |

The CLI attempts `json.loads()` first. On failure, the raw string is used.

## Configuration Snapshots

`ConfigProvider.snapshot(path)` persists the resolved configuration for
reproducibility. Call `snapshot()` before or after execution to capture the
exact parameters used in a run.
