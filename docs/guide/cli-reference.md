# CLI Reference

Meandra exposes four commands through the `meandra` CLI: `run`, `validate`,
`graph`, and `info`. All commands accept `--help` for inline documentation.

## Global Options

| Option | Short | Description |
|---|---|---|
| `--version` | `-V` | Print the package version and exit. |
| `--help` | | Show top-level help. |

```sh
meandra --version
meandra --help
```

## `meandra run`

Execute a workflow from a decorated pipeline class.

```sh
meandra run <pipeline> [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `pipeline` | Pipeline to run, in `module:ClassName` format (e.g. `mymodule:MyPipeline`). |

### Options

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--config` | `-c` | `PATH` | None | Path to a configuration file (JSON or YAML). |
| `--param` | `-p` | `TEXT` | None | Override a parameter as `key=value`. Repeatable. Values are parsed as JSON when possible; otherwise treated as strings. |
| `--output` | `-o` | `PATH` | None | Save workflow outputs to a JSON file instead of printing to stdout. |
| `--verbose` | `-v` | flag | `false` | Print pipeline name, node list, and inputs before execution; print traceback on failure. |

### Examples

Run with a YAML config:

```sh
meandra run analysis.pipeline:Main --config params.yaml
```

Override two parameters and save results:

```sh
meandra run analysis.pipeline:Main -p lr=0.001 -p epochs=50 -o results.json
```

Verbose execution for debugging:

```sh
meandra run analysis.pipeline:Main -v --config params.yaml
```

### Behavior

1. The CLI imports the pipeline class from the given module path.
2. `@pipeline`-decorated methods are assembled into a `Workflow`.
3. Configuration (if provided) loads from JSON or YAML.
4. Parameter overrides (`--param`) merge into the configuration dict. JSON-
   parseable values are converted automatically (numbers, booleans, arrays).
5. The workflow graph validates before execution.
6. `SchedulingOrchestrator` runs the workflow.
7. Outputs print as JSON to stdout, or write to the file specified by
   `--output`.

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | Successful execution. |
| 1 | Invalid pipeline path, import failure, validation error, or execution failure. |

---

## `meandra validate`

Validate a configuration file, optionally against a specific pipeline.

```sh
meandra validate <config> [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `config` | Path to the configuration file to validate (must exist). |

### Options

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--pipeline` | `-p` | `TEXT` | None | Pipeline to validate against, in `module:ClassName` format. When provided, the command checks that all required inputs are present. |
| `--verbose` | `-v` | flag | `false` | Print loaded keys and extra-key warnings. |

### Examples

Validate file syntax only:

```sh
meandra validate config.yaml
```

Validate against a pipeline's expected inputs:

```sh
meandra validate config.yaml --pipeline mymodule:MyPipeline
```

### Behavior

1. The configuration file loads as JSON or YAML.
2. Without `--pipeline`, the command confirms the file parses without error.
3. With `--pipeline`, the command also builds the workflow graph and compares
   required inputs against the configuration keys. Missing inputs produce
   warnings on stderr.

---

## `meandra graph`

Display or export the workflow dependency graph.

```sh
meandra graph <pipeline> [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `pipeline` | Pipeline to graph, in `module:ClassName` format. |

### Options

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | `PATH` | None | Save the graph to a file. The extension determines the format. |

### Supported Formats

| Extension | Requirement |
|---|---|
| `.dot` | None (native DOT output). |
| `.png` | Graphviz `dot` binary on `PATH`. |
| `.svg` | Graphviz `dot` binary on `PATH`. |
| `.pdf` | Graphviz `dot` binary on `PATH`. |

Without `--output`, the DOT representation prints to stdout.

### Examples

Print DOT to stdout:

```sh
meandra graph mymodule:MyPipeline
```

Export as PNG:

```sh
meandra graph mymodule:MyPipeline -o workflow.png
```

Export as DOT file:

```sh
meandra graph mymodule:MyPipeline -o workflow.dot
```

### DOT Output Structure

The generated graph uses `rankdir=LR` (left-to-right). Each node box displays
the node name, input keys, and output keys. Edges follow declared dependencies.

---

## `meandra info`

Print version and platform diagnostics.

```sh
meandra info
```

### Output Format

```
meandra <version> | Platform: <OS> Python <python_version>
```

### Example

```sh
$ meandra info
meandra 0.3.1 | Platform: Darwin Python 3.12.4
```
