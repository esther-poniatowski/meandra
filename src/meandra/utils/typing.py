"""
meandra.utils.typing
====================

Type checking utilities for runtime type validation.

Functions
---------
check_type
    Check if a value matches an expected type, supporting generics.
"""

from typing import Any, Dict, List, Type, Union, get_origin, get_args, Annotated, Literal
import typing


def check_type(value: Any, expected: Type) -> bool:
    """
    Check if a value matches an expected type, including generic types.

    Supports Optional, Union, List, Dict, and tuple types with proper
    handling of type arguments via `get_origin` and `get_args`.

    Parameters
    ----------
    value : Any
        The value to check.
    expected : Type
        The expected type, which may be a generic type.

    Returns
    -------
    bool
        True if the value matches the expected type.

    Examples
    --------
    >>> check_type(42, int)
    True
    >>> check_type(None, Optional[int])
    True
    >>> check_type([1, 2, 3], List[int])
    True
    >>> check_type({"a": 1}, Dict[str, int])
    True
    """
    if expected is Any:
        return True

    origin = get_origin(expected)
    args = get_args(expected)

    if origin is Annotated:
        return check_type(value, args[0])

    if origin is Literal:
        return value in args

    if origin is Union:
        return any(check_type(value, arg) for arg in args)

    if origin in (list, List):
        if not isinstance(value, list):
            return False
        if args:
            return all(check_type(item, args[0]) for item in value)
        return True

    if origin in (dict, Dict):
        if not isinstance(value, dict):
            return False
        if len(args) == 2:
            return all(
                check_type(k, args[0]) and check_type(v, args[1])
                for k, v in value.items()
            )
        return True

    if origin in (tuple,):
        if not isinstance(value, tuple):
            return False
        if args:
            # Handle Tuple[int, ...] (homogeneous variable-length)
            if len(args) == 2 and args[1] is Ellipsis:
                return all(check_type(item, args[0]) for item in value)
            # Handle Tuple[int, str, float] (heterogeneous fixed-length)
            if len(args) != len(value):
                return False
            return all(check_type(item, arg) for item, arg in zip(value, args))
        return True

    try:
        if isinstance(expected, type) and issubclass(expected, typing.Protocol):
            if getattr(expected, "_is_runtime_protocol", False):
                return isinstance(value, expected)
    except TypeError:
        pass

    return isinstance(value, expected)
