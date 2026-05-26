<a id="checkpoint"></a>

# Checkpoint

Workflow state persistence and resumption.

<a id="module-meandra.checkpoint.manager"></a>

<a id="manager"></a>

## Manager

<a id="meandra-checkpoint-manager"></a>

### meandra.checkpoint.manager

Checkpoint management for workflow resumption.

<a id="meandra.checkpoint.manager.CheckpointInfo"></a>

### *class* meandra.checkpoint.manager.CheckpointInfo(checkpoint_id, workflow_name, node_name, node_index, run_id, timestamp, workflow_hash=None, completed_nodes=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Summary information about a checkpoint.

<a id="meandra.checkpoint.manager.CheckpointInfo.checkpoint_id"></a>

#### checkpoint_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique checkpoint identifier.

<a id="meandra.checkpoint.manager.CheckpointInfo.workflow_name"></a>

#### workflow_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the workflow.

<a id="meandra.checkpoint.manager.CheckpointInfo.node_name"></a>

#### node_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the node that was checkpointed.

<a id="meandra.checkpoint.manager.CheckpointInfo.node_index"></a>

#### node_index *: [int](https://docs.python.org/3/library/functions.html#int)*

Index of the node in execution order.

<a id="meandra.checkpoint.manager.CheckpointInfo.run_id"></a>

#### run_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique run identifier.

<a id="meandra.checkpoint.manager.CheckpointInfo.timestamp"></a>

#### timestamp *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Timestamp of the checkpoint.

<a id="meandra.checkpoint.manager.CheckpointInfo.workflow_hash"></a>

#### workflow_hash *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Hash of the workflow structure at checkpoint time.

<a id="meandra.checkpoint.manager.CheckpointInfo.completed_nodes"></a>

#### completed_nodes *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Names of nodes completed before this checkpoint.

<a id="meandra.checkpoint.manager.Checkpoint"></a>

### *class* meandra.checkpoint.manager.Checkpoint(info, data, context, state)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A loaded checkpoint with data and metadata.

<a id="meandra.checkpoint.manager.Checkpoint.info"></a>

#### info *: [CheckpointInfo](#meandra.checkpoint.manager.CheckpointInfo)*

Summary information about the checkpoint.

<a id="meandra.checkpoint.manager.Checkpoint.data"></a>

#### data *: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*

Node output data.

<a id="meandra.checkpoint.manager.Checkpoint.context"></a>

#### context *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Execution context saved with the checkpoint.

<a id="meandra.checkpoint.manager.Checkpoint.state"></a>

#### state *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]]*

Workflow state at checkpoint time.

<a id="meandra.checkpoint.manager.ResumePlan"></a>

### *class* meandra.checkpoint.manager.ResumePlan(checkpoint_id, run_id, completed_nodes, context, state)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Explicit plan describing how a workflow may safely resume.

<a id="meandra.checkpoint.manager.ResumePlan.checkpoint_id"></a>

#### checkpoint_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Identifier of the checkpoint to resume from.

<a id="meandra.checkpoint.manager.ResumePlan.run_id"></a>

#### run_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Run identifier for the resumed execution.

<a id="meandra.checkpoint.manager.ResumePlan.completed_nodes"></a>

#### completed_nodes *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Names of nodes already completed.

<a id="meandra.checkpoint.manager.ResumePlan.context"></a>

#### context *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

Execution context to restore.

<a id="meandra.checkpoint.manager.ResumePlan.state"></a>

#### state *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]]*

Workflow state to restore.

<a id="meandra.checkpoint.manager.CheckpointManager"></a>

### *class* meandra.checkpoint.manager.CheckpointManager(storage)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Manage workflow checkpoints for resumption.

The checkpoint manager provides a high-level interface for saving,
loading, and managing checkpoints during workflow execution.

* **Parameters:**
  **storage** ([*CheckpointStorage*](#meandra.checkpoint.storage.CheckpointStorage)) – Storage backend for checkpoints.

### Examples

```pycon
>>> from meandra.checkpoint import CheckpointManager, FileSystemStorage
>>> storage = FileSystemStorage("/tmp/checkpoints")
>>> manager = CheckpointManager(storage)
>>>
>>> # Save a checkpoint
>>> manager.save("my_workflow", "node1", 0, {"output": data}, "run_001")
>>>
>>> # Load latest checkpoint
>>> checkpoint = manager.load_latest("my_workflow")
>>> if checkpoint:
...     print(f"Resuming from node {checkpoint.info.node_name}")
```

<a id="meandra.checkpoint.manager.CheckpointManager.with_filesystem"></a>

#### *classmethod* with_filesystem(base_dir, retention=5)

Create a checkpoint manager with filesystem storage.

* **Parameters:**
  * **base_dir** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Base directory for checkpoint storage.
  * **retention** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Number of checkpoints to retain per workflow.
* **Returns:**
  Manager with `FileSystemStorage` backend.
* **Return type:**
  [CheckpointManager](#meandra.checkpoint.manager.CheckpointManager)

<a id="meandra.checkpoint.manager.CheckpointManager.save"></a>

#### save(workflow_name, node_name, node_index, data, run_id, context=None, workflow_hash=None, workflow_state=None, completed_nodes=None)

Save a checkpoint after node execution.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node that produced the data.
  * **node_index** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Index of the node in execution order.
  * **data** (*Any*) – Node output data to checkpoint.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique run identifier.
  * **context** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]*) – Full execution context to save for resumption.
  * **workflow_hash** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Hash of the workflow structure for compatibility checks.
  * **workflow_state** (*Optional* *[**Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Dict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Any* *]* *]* *]*) – Full workflow state to persist.
  * **completed_nodes** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Names of nodes completed so far.
* **Returns:**
  Checkpoint identifier.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="meandra.checkpoint.manager.CheckpointManager.load"></a>

#### load(checkpoint_id)

Load a specific checkpoint.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.
* **Returns:**
  Loaded checkpoint, or None if not found.
* **Return type:**
  Optional[[Checkpoint](#meandra.checkpoint.manager.Checkpoint)]

<a id="meandra.checkpoint.manager.CheckpointManager.load_latest"></a>

#### load_latest(workflow_name)

Load the most recent checkpoint for a workflow.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
* **Returns:**
  Most recent checkpoint, or None if none exist.
* **Return type:**
  Optional[[Checkpoint](#meandra.checkpoint.manager.Checkpoint)]

<a id="meandra.checkpoint.manager.CheckpointManager.load_for_run"></a>

#### load_for_run(workflow_name, run_id)

Load the most recent checkpoint for a specific run.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Run identifier to match.
* **Returns:**
  Most recent checkpoint for the run, or None if none exist.
* **Return type:**
  Optional[[Checkpoint](#meandra.checkpoint.manager.Checkpoint)]

<a id="meandra.checkpoint.manager.CheckpointManager.list_checkpoints"></a>

#### list_checkpoints(workflow_name)

List all checkpoints for a workflow.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
* **Returns:**
  List of checkpoint metadata, sorted by timestamp (newest first).
* **Return type:**
  List[[CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)]

<a id="meandra.checkpoint.manager.CheckpointManager.delete"></a>

#### delete(checkpoint_id)

Delete a checkpoint.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.

<a id="meandra.checkpoint.manager.CheckpointManager.clear_workflow"></a>

#### clear_workflow(workflow_name)

Delete all checkpoints for a workflow.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
* **Returns:**
  Number of checkpoints deleted.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="meandra.checkpoint.manager.CheckpointManager.build_resume_plan"></a>

#### build_resume_plan(workflow, checkpoint)

Validate checkpoint compatibility and build an explicit resume plan.

* **Parameters:**
  * **workflow** ([*Workflow*](core.md#meandra.core.workflow.Workflow)) – The workflow to resume.
  * **checkpoint** ([*Checkpoint*](#meandra.checkpoint.manager.Checkpoint)) – The checkpoint to resume from.
* **Returns:**
  Plan describing how the workflow may safely resume.
* **Return type:**
  [ResumePlan](#meandra.checkpoint.manager.ResumePlan)

<a id="module-meandra.checkpoint.storage"></a>

<a id="storage"></a>

## Storage

<a id="meandra-checkpoint-storage"></a>

### meandra.checkpoint.storage

Storage backends for checkpoints.

<a id="meandra.checkpoint.storage.CheckpointMetadata"></a>

### *class* meandra.checkpoint.storage.CheckpointMetadata(checkpoint_id, workflow_name, node_name, node_index, run_id, timestamp, data_path, workflow_hash=None, completed_nodes=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Metadata for a checkpoint.

<a id="meandra.checkpoint.storage.CheckpointMetadata.checkpoint_id"></a>

#### checkpoint_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique identifier for the checkpoint.

<a id="meandra.checkpoint.storage.CheckpointMetadata.workflow_name"></a>

#### workflow_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the workflow.

<a id="meandra.checkpoint.storage.CheckpointMetadata.node_name"></a>

#### node_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the node that produced the data.

<a id="meandra.checkpoint.storage.CheckpointMetadata.node_index"></a>

#### node_index *: [int](https://docs.python.org/3/library/functions.html#int)*

Index of the node in execution order.

<a id="meandra.checkpoint.storage.CheckpointMetadata.run_id"></a>

#### run_id *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Unique run identifier.

<a id="meandra.checkpoint.storage.CheckpointMetadata.timestamp"></a>

#### timestamp *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

ISO-format timestamp of checkpoint creation.

<a id="meandra.checkpoint.storage.CheckpointMetadata.data_path"></a>

#### data_path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Path to the serialized data file.

<a id="meandra.checkpoint.storage.CheckpointMetadata.workflow_hash"></a>

#### workflow_hash *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Hash of the workflow definition, or None.

<a id="meandra.checkpoint.storage.CheckpointMetadata.completed_nodes"></a>

#### completed_nodes *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]* *= None*

Names of nodes completed at checkpoint time.

<a id="meandra.checkpoint.storage.CheckpointMetadata.to_dict"></a>

#### to_dict()

Convert to dictionary.

* **Returns:**
  Dictionary representation of the metadata.
* **Return type:**
  [dict](https://docs.python.org/3/library/stdtypes.html#dict)

<a id="meandra.checkpoint.storage.CheckpointMetadata.from_dict"></a>

#### *classmethod* from_dict(data)

Create from dictionary.

* **Parameters:**
  **data** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – Dictionary containing checkpoint metadata fields.
* **Returns:**
  New instance populated from the dictionary.
* **Return type:**
  [CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)

<a id="meandra.checkpoint.storage.CheckpointStorage"></a>

### *class* meandra.checkpoint.storage.CheckpointStorage

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for checkpoint storage backends.

Storage backends handle the persistence of checkpoint data and metadata.

<a id="meandra.checkpoint.storage.CheckpointStorage.save"></a>

#### *abstractmethod* save(workflow_name, node_name, node_index, data, run_id, workflow_hash=None, completed_nodes=None)

Save checkpoint data.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node that produced the data.
  * **node_index** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Index of the node in execution order.
  * **data** (*Any*) – Data to checkpoint.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique run identifier.
  * **workflow_hash** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Hash of the workflow definition.
  * **completed_nodes** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Names of nodes completed so far.
* **Returns:**
  Checkpoint identifier.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="meandra.checkpoint.storage.CheckpointStorage.load"></a>

#### *abstractmethod* load(checkpoint_id)

Load checkpoint data.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.checkpoint.storage.CheckpointStorage.list_checkpoints"></a>

#### *abstractmethod* list_checkpoints(workflow_name)

List all checkpoints for a workflow.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
* **Returns:**
  List of checkpoint metadata, sorted by timestamp (newest first).
* **Return type:**
  List[[CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)]

<a id="meandra.checkpoint.storage.CheckpointStorage.delete"></a>

#### *abstractmethod* delete(checkpoint_id)

Delete a checkpoint.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.

<a id="meandra.checkpoint.storage.CheckpointStorage.get_metadata"></a>

#### *abstractmethod* get_metadata(checkpoint_id)

Get metadata for a checkpoint.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.
* **Returns:**
  Checkpoint metadata, or None if not found.
* **Return type:**
  Optional[[CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)]

<a id="meandra.checkpoint.storage.FileSystemStorage"></a>

### *class* meandra.checkpoint.storage.FileSystemStorage(base_dir, retention=0)

Bases: [`CheckpointStorage`](#meandra.checkpoint.storage.CheckpointStorage)

File system-based checkpoint storage.

Stores checkpoint data as gzip-compressed pickle files with JSON metadata.

Directory structure:
: base_dir/
  : workflow_name/
    : checkpoint_<timestamp>_<run_id>/
      : metadata.json
        data.pkl.gz

* **Parameters:**
  * **base_dir** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *Path*) – Base directory for checkpoint storage.
  * **retention** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Number of checkpoints to retain per workflow (0 = unlimited).

### Examples

```pycon
>>> storage = FileSystemStorage("/tmp/checkpoints", retention=5)
>>> checkpoint_id = storage.save("my_workflow", "node1", 0, data, "run_001")
>>> loaded_data = storage.load(checkpoint_id)
```

<a id="meandra.checkpoint.storage.FileSystemStorage.save"></a>

#### save(workflow_name, node_name, node_index, data, run_id, workflow_hash=None, completed_nodes=None)

Save checkpoint data to filesystem.

* **Parameters:**
  * **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
  * **node_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the node that produced the data.
  * **node_index** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Index of the node in execution order.
  * **data** (*Any*) – Data to checkpoint.
  * **run_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique run identifier.
  * **workflow_hash** (*Optional* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Hash of the workflow definition.
  * **completed_nodes** (*Optional* *[**List* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *]*) – Names of nodes completed so far.
* **Returns:**
  Checkpoint identifier.
* **Return type:**
  [str](https://docs.python.org/3/library/stdtypes.html#str)

<a id="meandra.checkpoint.storage.FileSystemStorage.load"></a>

#### load(checkpoint_id)

Load checkpoint data from filesystem.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.
* **Returns:**
  Loaded data.
* **Return type:**
  Any

<a id="meandra.checkpoint.storage.FileSystemStorage.list_checkpoints"></a>

#### list_checkpoints(workflow_name)

List all checkpoints for a workflow.

* **Parameters:**
  **workflow_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the workflow.
* **Returns:**
  List of checkpoint metadata, sorted by timestamp (newest first).
* **Return type:**
  List[[CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)]

<a id="meandra.checkpoint.storage.FileSystemStorage.delete"></a>

#### delete(checkpoint_id)

Delete a checkpoint from filesystem.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.

<a id="meandra.checkpoint.storage.FileSystemStorage.get_metadata"></a>

#### get_metadata(checkpoint_id)

Get metadata for a checkpoint.

* **Parameters:**
  **checkpoint_id** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Checkpoint identifier.
* **Returns:**
  Checkpoint metadata, or None if not found.
* **Return type:**
  Optional[[CheckpointMetadata](#meandra.checkpoint.storage.CheckpointMetadata)]
