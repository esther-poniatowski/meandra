<a id="configuration"></a>

# Configuration

Configuration management for workflows.

<a id="module-meandra.configuration.mod"></a>

<a id="configuration-provider"></a>

## Configuration Provider

<a id="meandra-configuration"></a>

### meandra.configuration

Configuration provider interface for Meandra.

<a id="meandra.configuration.mod.ConfigProvider"></a>

### *class* meandra.configuration.mod.ConfigProvider(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Minimal configuration provider interface.

Implementations should adapt Hydra, Tessara, or custom config systems.

<a id="meandra.configuration.mod.ConfigProvider.get"></a>

#### get(path)

Retrieve a value by dotted path.

* **Parameters:**
  **path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Dotted configuration path (e.g. `"training.lr"`).

<a id="meandra.configuration.mod.ConfigProvider.to_dict"></a>

#### to_dict()

Return a resolved dictionary representation.

<a id="meandra.configuration.mod.ConfigProvider.resolve"></a>

#### resolve()

Resolve interpolations or dynamic values.

<a id="meandra.configuration.mod.ConfigProvider.snapshot"></a>

#### snapshot(path)

Persist a configuration snapshot.

* **Parameters:**
  **path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Filesystem path where the snapshot is written.
