# CLI Reference

Meandra exposes four commands through the `meandra` CLI: `run`, `validate`,
`graph`, and `info`. All commands accept `--help` for inline documentation.

The options follow the
[command-line conventions](https://github.com/esther-poniatowski/keystone/blob/main/docs/internals/cli-conventions.md)
of the workspace. Meandra has no settings file and works on no project root,
so it offers neither `--config` nor `--root`. A path given on the command line
is relative to the current folder. A command overwrites the file named by
`--output`, since it derives that file and can regenerate it.

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success. |
| 1 | A validation or a run finds a problem: an invalid workflow graph, missing inputs, a failed execution, or a failed Graphviz export. |
| 2 | A usage error: an unknown option, a malformed `--param`, an invalid pipeline path, a class without `@pipeline`, a missing or unreadable inputs file, or an unknown graph format. |

## Global Options

| Option | Short | Description |
|---|---|---|
| `--version` | `-v` | Print the package version and exit. |
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
| `--inputs` | `-i` | `PATH` | None | Path to the inputs file of the run (JSON or YAML), relative to the current folder. |
| `--param` | `-p` | `TEXT` | None | Override a parameter as `key=value`. Repeatable. Values are parsed as JSON when possible; otherwise treated as strings. |
| `--output` | `-o` | `PATH` | None | Save workflow outputs to a JSON file instead of printing to stdout. |
| `--verbose` | | flag | `false` | Print pipeline name, node list, and inputs before execution; print traceback on failure. |

### Examples

Run with a YAML inputs file:

```sh
meandra run analysis.pipeline:Main --inputs params.yaml
```

Override two parameters and save results:

```sh
meandra run analysis.pipeline:Main -p lr=0.001 -p epochs=50 -o results.json
```

Verbose execution for debugging:

```sh
meandra run analysis.pipeline:Main --verbose --inputs params.yaml
```

### Behavior

1. The CLI imports the pipeline class from the given module path.
2. `@pipeline`-decorated methods are assembled into a `Workflow`.
3. The inputs file (if provided) loads from JSON or YAML.
4. Parameter overrides (`--param`) merge into the inputs dict. JSON-
   parseable values are converted automatically (numbers, booleans, arrays).
5. The workflow graph validates before execution.
6. `SchedulingOrchestrator` runs the workflow.
7. Outputs print as JSON to stdout, or write to the file specified by
   `--output`.

---

## `meandra validate`

Validate an inputs file, optionally against a specific pipeline.

```sh
meandra validate <inputs> [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `inputs` | Path to the inputs file to validate (must exist). |

### Options

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--pipeline` | `-p` | `TEXT` | None | Pipeline to validate against, in `module:ClassName` format. When provided, the command checks that all required inputs are present. |
| `--verbose` | | flag | `false` | Print loaded keys and extra keys. |

### Examples

Validate file syntax only:

```sh
meandra validate inputs.yaml
```

Validate against a pipeline's expected inputs:

```sh
meandra validate inputs.yaml --pipeline mymodule:MyPipeline
```

### Behavior

1. The inputs file loads as JSON or YAML.
2. Without `--pipeline`, the command confirms the file parses without error.
3. With `--pipeline`, the command also builds the workflow graph and compares
   required inputs against the keys of the file. Missing inputs produce an
   error on stderr and the exit status 1.

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
