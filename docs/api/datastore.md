<a id="datastore"></a>

# Datastore

Data I/O handlers and dataset catalog.

<a id="module-meandra.datastore.catalog"></a>

<a id="catalog"></a>

## Catalog

<a id="meandra-datastore-catalog"></a>

### meandra.datastore.catalog

Data catalog for named dataset management.

<a id="meandra.datastore.catalog.DatasetEntry"></a>

### *class* meandra.datastore.catalog.DatasetEntry(name, path_template, handler=None, description='', metadata=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Entry in the data catalog.

<a id="meandra.datastore.catalog.DatasetEntry.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Logical name for the dataset.

<a id="meandra.datastore.catalog.DatasetEntry.path_template"></a>

#### path_template *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Path template with optional placeholders.

<a id="meandra.datastore.catalog.DatasetEntry.handler"></a>

#### handler *: [IOHandler](#meandra.datastore.io_handlers.IOHandler) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Handler for this dataset.

<a id="meandra.datastore.catalog.DatasetEntry.description"></a>

#### description *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Description of the dataset.

<a id="meandra.datastore.catalog.DatasetEntry.metadata"></a>

#### metadata *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Additional metadata for the entry.

<a id="meandra.datastore.catalog.DatasetEntry.resolve_path"></a>

#### resolve_path(\*\*kwargs)

Resolve path template with provided values.

Supports placeholders: {run_id}, {date}, {timestamp}, and custom keys.

* **Parameters:**
  **\*\*kwargs** (*Any*) – Values to substitute into the path template.
* **Returns:**
  Resolved path.
* **Return type:**
  Path

<a id="meandra.datastore.catalog.DatasetEntry.required_placeholders"></a>

#### required_placeholders()

Return required placeholders in the path template.

Placeholders with defaults (date, timestamp) are excluded.

* **Returns:**
  Set of required placeholder keys.
* **Return type:**
  Set[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.datastore.catalog.DataCatalog"></a>

### *class* meandra.datastore.catalog.DataCatalog(base_dir=None, registry=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Named dataset registry with path templating.

The data catalog provides a central registry for datasets, mapping
logical names to file paths and handlers. It supports path templating
for dynamic path resolution.

* **Parameters:**
  * **base_dir** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *Path* *]*) – Base directory for relative paths.
  * **registry** (*Optional* *[*[*HandlerRegistry*](#meandra.datastore.io_handlers.HandlerRegistry) *]*) – Handler registry for format detection.

### Examples

```pycon
>>> catalog = DataCatalog("/data")
>>>
>>> # Register datasets
>>> catalog.register("raw_data", "{run_id}/raw.npy")
>>> catalog.register("processed", "{run_id}/processed.pkl", description="Processed output")
>>>
>>> # Save and load data
>>> catalog.save("raw_data", data, run_id="run_001")
>>> loaded = catalog.load("raw_data", run_id="run_001")
```

With explicit handler:

```pycon
>>> from meandra.datastore import JSONHandler
>>> catalog.register("config", "config.json", handler=JSONHandler())
```

<a id="meandra.datastore.catalog.DataCatalog.register"></a>

#### register(name, path_template, handler=None, description='', \*\*metadata)

Register a dataset in the catalog.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Logical name for the dataset.
  * **path_template** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Path template with optional placeholders ({run_id}, {date}, etc.).
    Relative paths are resolved against base_dir.
  * **handler** (*Optional* *[*[*IOHandler*](#meandra.datastore.io_handlers.IOHandler) *]*) – Handler for this dataset. If None, inferred from extension.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Optional description of the dataset.
  * **\*\*metadata** (*Any*) – Additional metadata to store with the entry.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If a dataset with the same name is already registered.

<a id="meandra.datastore.catalog.DataCatalog.unregister"></a>

#### unregister(name)

Remove a dataset from the catalog.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset to remove.

<a id="meandra.datastore.catalog.DataCatalog.get_entry"></a>

#### get_entry(name)

Get a dataset entry by name.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset.
* **Returns:**
  The dataset entry.
* **Return type:**
  [DatasetEntry](#meandra.datastore.catalog.DatasetEntry)
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If dataset is not registered.

<a id="meandra.datastore.catalog.DataCatalog.get_path"></a>

#### get_path(name, \*\*kwargs)

Get the resolved path for a dataset.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset.
  * **\*\*kwargs** (*Any*) – Values for path template placeholders.
* **Returns:**
  Resolved path.
* **Return type:**
  Path

<a id="meandra.datastore.catalog.DataCatalog.save"></a>

#### save(name, data, \*\*kwargs)

Save data to a registered dataset.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset.
  * **data** (*Any*) – Data to save.
  * **\*\*kwargs** (*Any*) – Values for path template placeholders.
* **Returns:**
  Path where data was saved.
* **Return type:**
  Path

<a id="meandra.datastore.catalog.DataCatalog.load"></a>

#### load(name, \*\*kwargs)

Load data from a registered dataset.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset.
  * **\*\*kwargs** (*Any*) – Values for path template placeholders.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.datastore.catalog.DataCatalog.exists"></a>

#### exists(name, \*\*kwargs)

Check if a dataset file exists.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dataset.
  * **\*\*kwargs** (*Any*) – Values for path template placeholders.
* **Returns:**
  True if the file exists.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.datastore.catalog.DataCatalog.list_datasets"></a>

#### list_datasets()

List all registered datasets.

* **Returns:**
  Mapping of names to dataset entries.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), [DatasetEntry](#meandra.datastore.catalog.DatasetEntry)]

<a id="meandra.datastore.catalog.DataCatalog.required_placeholders"></a>

#### required_placeholders(name=None)

Return required placeholders for one dataset or all datasets.

* **Parameters:**
  **name** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – If provided, return placeholders for a single dataset.
* **Returns:**
  Placeholder keys per dataset, or a single set for one dataset.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), Set[[str](https://docs.python.org/3/library/stdtypes.html#str)]] | Set[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="module-meandra.datastore.io_handlers"></a>

<a id="io-handlers"></a>

## IO Handlers

<a id="meandra-datastore-io-handlers"></a>

### meandra.datastore.io_handlers

I/O handlers for various file formats.

<a id="meandra.datastore.io_handlers.IOHandler"></a>

### *class* meandra.datastore.io_handlers.IOHandler

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for file I/O operations.

Each handler supports specific file formats and provides read/write
operations for data persistence.

<a id="meandra.datastore.io_handlers.IOHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= []*

File extensions this handler supports.

<a id="meandra.datastore.io_handlers.IOHandler.supports"></a>

#### *classmethod* supports(path)

Check if this handler supports the given file path.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  True if this handler supports the file extension.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="meandra.datastore.io_handlers.IOHandler.read"></a>

#### *abstractmethod* read(path)

Read data from a file.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.IOHandler.write"></a>

#### *abstractmethod* write(path, data)

Write data to a file.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.PickleHandler"></a>

### *class* meandra.datastore.io_handlers.PickleHandler

Bases: [`IOHandler`](#meandra.datastore.io_handlers.IOHandler)

Handler for Python pickle files.

Supports arbitrary Python objects via pickle serialization.

### Examples

```pycon
>>> handler = PickleHandler()
>>> handler.write("data.pkl", {"key": [1, 2, 3]})
>>> data = handler.read("data.pkl")
```

<a id="meandra.datastore.io_handlers.PickleHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ['.pkl', '.pickle']*

File extensions this handler supports.

<a id="meandra.datastore.io_handlers.PickleHandler.read"></a>

#### read(path)

Read pickled data from file.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Deserialized Python object.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.PickleHandler.write"></a>

#### write(path, data)

Write data to pickle file.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.NumpyHandler"></a>

### *class* meandra.datastore.io_handlers.NumpyHandler

Bases: [`IOHandler`](#meandra.datastore.io_handlers.IOHandler)

Handler for NumPy array files.

Supports .npy (single array) and .npz (multiple arrays) formats.

### Examples

```pycon
>>> handler = NumpyHandler()
>>> handler.write("array.npy", np.array([1, 2, 3]))
>>> arr = handler.read("array.npy")
```

<a id="meandra.datastore.io_handlers.NumpyHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ['.npy', '.npz']*

File extensions this handler supports.

<a id="meandra.datastore.io_handlers.NumpyHandler.read"></a>

#### read(path)

Read NumPy array(s) from file.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Loaded array or dict of arrays.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.NumpyHandler.write"></a>

#### write(path, data)

Write NumPy array(s) to file.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.JSONHandler"></a>

### *class* meandra.datastore.io_handlers.JSONHandler(indent=2)

Bases: [`IOHandler`](#meandra.datastore.io_handlers.IOHandler)

Handler for JSON files.

Suitable for configuration and simple nested structures.

* **Parameters:**
  **indent** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Number of spaces for JSON indentation.

### Examples

```pycon
>>> handler = JSONHandler()
>>> handler.write("config.json", {"key": "value"})
>>> data = handler.read("config.json")
```

<a id="meandra.datastore.io_handlers.JSONHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ['.json']*

File extensions this handler supports.

<a id="meandra.datastore.io_handlers.JSONHandler.read"></a>

#### read(path)

Read JSON data from file.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Deserialized JSON data.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.JSONHandler.write"></a>

#### write(path, data)

Write data to JSON file.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.YAMLHandler"></a>

### *class* meandra.datastore.io_handlers.YAMLHandler

Bases: [`IOHandler`](#meandra.datastore.io_handlers.IOHandler)

Handler for YAML files.

Suitable for configuration and human-readable data.

### Examples

```pycon
>>> handler = YAMLHandler()
>>> handler.write("config.yaml", {"key": "value"})
>>> data = handler.read("config.yaml")
```

<a id="meandra.datastore.io_handlers.YAMLHandler.EXTENSIONS"></a>

#### EXTENSIONS *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ['.yaml', '.yml']*

File extensions this handler supports.

<a id="meandra.datastore.io_handlers.YAMLHandler.read"></a>

#### read(path)

Read YAML data from file.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
* **Returns:**
  Deserialized YAML data.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.YAMLHandler.write"></a>

#### write(path, data)

Write data to YAML file.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – Path to the file.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.HandlerRegistry"></a>

### *class* meandra.datastore.io_handlers.HandlerRegistry(register_defaults=True)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Registry of IOHandlers by file extension.

Provides isolation for handler registration, avoiding global state.
Each registry instance maintains its own set of handlers.

* **Parameters:**
  **register_defaults** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, register default handlers on creation.

### Examples

```pycon
>>> registry = HandlerRegistry()
>>> registry.register(PickleHandler())
>>> handler = registry.get_handler("data.pkl")
```

<a id="meandra.datastore.io_handlers.HandlerRegistry.register"></a>

#### register(handler)

Register a handler for its supported extensions.

* **Parameters:**
  **handler** ([*IOHandler*](#meandra.datastore.io_handlers.IOHandler)) – Handler to register.

<a id="meandra.datastore.io_handlers.HandlerRegistry.register_defaults"></a>

#### register_defaults()

Register the default handlers (Pickle, Numpy, JSON, YAML).

<a id="meandra.datastore.io_handlers.HandlerRegistry.get_handler"></a>

#### get_handler(path)

Get appropriate handler for a file path.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
* **Returns:**
  Handler for the file format.
* **Return type:**
  [IOHandler](#meandra.datastore.io_handlers.IOHandler)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If no handler supports the file extension.

<a id="meandra.datastore.io_handlers.HandlerRegistry.read"></a>

#### read(path)

Read data from a file using the appropriate handler.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.HandlerRegistry.write"></a>

#### write(path, data)

Write data to a file using the appropriate handler.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
  * **data** (*Any*) – Data to write.

<a id="meandra.datastore.io_handlers.HandlerRegistry.clear"></a>

#### clear()

Clear all registered handlers.

<a id="meandra.datastore.io_handlers.HandlerRegistry.extensions"></a>

#### *property* extensions *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

List of registered extensions.

* **Returns:**
  Registered file extensions.
* **Return type:**
  List[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="meandra.datastore.io_handlers.register_handler"></a>

### meandra.datastore.io_handlers.register_handler(handler)

Register a handler in the default registry.

* **Parameters:**
  **handler** ([*IOHandler*](#meandra.datastore.io_handlers.IOHandler)) – Handler to register.

<a id="meandra.datastore.io_handlers.register_default_handlers"></a>

### meandra.datastore.io_handlers.register_default_handlers()

Register the default handlers if none are registered.

<a id="meandra.datastore.io_handlers.reset_default_registry"></a>

### meandra.datastore.io_handlers.reset_default_registry()

Reset the default registry to a fresh state with default handlers.

Useful for test isolation – ensures no cross-test handler leakage.

<a id="meandra.datastore.io_handlers.get_handler"></a>

### meandra.datastore.io_handlers.get_handler(path)

Get appropriate handler for a file path.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
* **Returns:**
  Handler for the file format.
* **Return type:**
  [IOHandler](#meandra.datastore.io_handlers.IOHandler)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If no handler supports the file extension.

<a id="meandra.datastore.io_handlers.read_file"></a>

### meandra.datastore.io_handlers.read_file(path)

Read data from a file using the appropriate handler.

* **Parameters:**
  **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.datastore.io_handlers.write_file"></a>

### meandra.datastore.io_handlers.write_file(path, data)

Write data to a file using the appropriate handler.

* **Parameters:**
  * **path** (*Union* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Path* *]*) – File path.
  * **data** (*Any*) – Data to write.
