<a id="utilities"></a>

# Utilities

Internal helpers and shared typing utilities.

<a id="module-meandra.utils.mod"></a>

<a id="helpers"></a>

## Helpers

<a id="meandra-utils"></a>

### meandra.utils

Placeholder module for utility helpers.

<a id="module-meandra.utils.typing"></a>

<a id="typing"></a>

## Typing

<a id="meandra-utils-typing"></a>

### meandra.utils.typing

Type checking utilities for runtime type validation.

<a id="meandra.utils.typing.check_type"></a>

### meandra.utils.typing.check_type(value, expected)

Check if a value matches an expected type, including generic types.

Supports Optional, Union, List, Dict, and tuple types with proper
handling of type arguments via get_origin and get_args.

* **Parameters:**
  * **value** (*Any*) – The value to check.
  * **expected** (*Type*) – The expected type, which may be a generic type.
* **Returns:**
  True if the value matches the expected type.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

### Examples

```pycon
>>> check_type(42, int)
True
>>> check_type(None, Optional[int])
True
>>> check_type([1, 2, 3], List[int])
True
>>> check_type({"a": 1}, Dict[str, int])
True
```
