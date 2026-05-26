<a id="logging"></a>

# Logging

Logging configuration and contextual logging helpers.

<a id="module-meandra.logging.config"></a>

<a id="configuration"></a>

## Configuration

<a id="meandra-logging-config"></a>

### meandra.logging.config

Logging configuration and utilities.

<a id="meandra.logging.config.LogLevel"></a>

### *class* meandra.logging.config.LogLevel(\*values)

Bases: [`str`](https://docs.python.org/3/library/stdtypes.html#str), [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Log level enumeration.

<a id="meandra.logging.config.LogLevel.DEBUG"></a>

#### DEBUG *= 'DEBUG'*

<a id="meandra.logging.config.LogLevel.INFO"></a>

#### INFO *= 'INFO'*

<a id="meandra.logging.config.LogLevel.WARNING"></a>

#### WARNING *= 'WARNING'*

<a id="meandra.logging.config.LogLevel.ERROR"></a>

#### ERROR *= 'ERROR'*

<a id="meandra.logging.config.LogLevel.CRITICAL"></a>

#### CRITICAL *= 'CRITICAL'*

<a id="meandra.logging.config.StructuredFormatter"></a>

### *class* meandra.logging.config.StructuredFormatter(fmt=None, datefmt=None, include_context=True)

Bases: [`Formatter`](https://docs.python.org/3/library/logging.html#logging.Formatter)

Formatter that includes structured context in log messages.

Injects workflow execution context (run_id, workflow_name, node_name)
when available.

* **Parameters:**
  * **fmt** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Log format string. If None, uses a default structured format.
  * **datefmt** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Date format string. If None, uses `%Y-%m-%d %H:%M:%S`.
  * **include_context** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to include workflow context in log messages. Default True.

<a id="meandra.logging.config.StructuredFormatter.__init__"></a>

#### \_\_init_\_(fmt=None, datefmt=None, include_context=True)

Initialize the structured formatter.

<a id="meandra.logging.config.StructuredFormatter.format"></a>

#### format(record)

Format a log record with optional workflow context.

* **Parameters:**
  **record** ([*logging.LogRecord*](https://docs.python.org/3/library/logging.html#logging.LogRecord)) – The log record to format.
* **Returns:**
  Formatted log message.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="meandra.logging.config.configure_logging"></a>

### meandra.logging.config.configure_logging(level=LogLevel.INFO, stream=None, log_file=None, include_context=True, format_string=None)

Configure logging for Meandra.

* **Parameters:**
  * **level** ([*LogLevel*](#meandra.logging.config.LogLevel) *|* [*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Minimum log level. Default is INFO.
  * **stream** (*Optional* *[**TextIO* *]*) – Stream for console output. Default is sys.stderr.
  * **log_file** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Path to log file. If provided, logs are also written to file.
  * **include_context** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Whether to include workflow context in log messages. Default True.
  * **format_string** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Custom format string. If None, uses structured format.

### Examples

```pycon
>>> from meandra.logging import configure_logging, LogLevel
>>> configure_logging(level=LogLevel.DEBUG, log_file="workflow.log")
```

<a id="meandra.logging.config.get_logger"></a>

### meandra.logging.config.get_logger(name)

Get a logger for a Meandra module.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Logger name (typically \_\_name_\_ of the module).
* **Returns:**
  Configured logger instance.
* **Return type:**
  [logging.Logger](https://docs.python.org/3/library/logging.html#logging.Logger)

### Examples

```pycon
>>> from meandra.logging import get_logger
>>> logger = get_logger(__name__)
>>> logger.info("Processing started")
```

<a id="module-meandra.logging.context"></a>

<a id="context"></a>

## Context

<a id="meandra-logging-context"></a>

### meandra.logging.context

Execution context for structured logging.

<a id="meandra.logging.context.LogContext"></a>

### *class* meandra.logging.context.LogContext(run_id=None, workflow_name=None, node_name=None, start_time=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Execution context for workflow logging.

Stores information about the current execution state for
injection into log messages.

<a id="meandra.logging.context.LogContext.run_id"></a>

#### run_id *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Unique identifier for the current run.

<a id="meandra.logging.context.LogContext.workflow_name"></a>

#### workflow_name *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Name of the currently executing workflow.

<a id="meandra.logging.context.LogContext.node_name"></a>

#### node_name *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Name of the currently executing node.

<a id="meandra.logging.context.LogContext.start_time"></a>

#### start_time *: [float](https://docs.python.org/3/library/functions.html#float) | [None](https://docs.python.org/3/library/constants.html#None)*

Unix timestamp when execution started.

<a id="meandra.logging.context.LogContext.elapsed_seconds"></a>

#### *property* elapsed_seconds *: [float](https://docs.python.org/3/library/functions.html#float)*

Return elapsed time since start in seconds.

* **Returns:**
  Elapsed time in seconds.
* **Return type:**
  [float](https://docs.python.org/3/library/functions.html#float)

<a id="meandra.logging.context.LogContext.with_node"></a>

#### with_node(node_name)

Create a new context with the specified node.

* **Parameters:**
  **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node.
* **Returns:**
  New context with the node set.
* **Return type:**
  [LogContext](#meandra.logging.context.LogContext)

<a id="meandra.logging.context.LogContext.with_workflow"></a>

#### with_workflow(workflow_name, run_id)

Create a new context with workflow information.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique identifier for the run.
* **Returns:**
  New context with workflow information.
* **Return type:**
  [LogContext](#meandra.logging.context.LogContext)

<a id="meandra.logging.context.LogContext.current"></a>

#### *classmethod* current()

Get the current context.

* **Returns:**
  The current log context.
* **Return type:**
  [LogContext](#meandra.logging.context.LogContext)

<a id="meandra.logging.context.LogContext.set_current"></a>

#### *classmethod* set_current(context)

Set the current context.

* **Parameters:**
  **context** ([*LogContext*](#meandra.logging.context.LogContext)) – The context to set as current.

<a id="meandra.logging.context.LogContext.clear"></a>

#### *classmethod* clear()

Clear the current context, resetting to defaults.

<a id="meandra.logging.context.LogContextManager"></a>

### *class* meandra.logging.context.LogContextManager(run_id=None, workflow_name=None, node_name=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Context manager for scoped log context.

* **Parameters:**
  * **run_id** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Unique identifier for the current run.
  * **workflow_name** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Name of the currently executing workflow.
  * **node_name** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Name of the currently executing node.

### Examples

```pycon
>>> with LogContextManager(workflow_name="my_workflow", run_id="abc123"):
...     logger.info("Inside workflow context")
```
