#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.core.parameters
=======================

Classes
-------
Param
    Define a parameter with properties and constraints for runtime validation.
ParameterSet
    Manage a collection of parameters.

"""
from collections import UserDict
from collections.abc import Iterable
from itertools import product
import re
from typing import Any, Callable, Optional, Self, Dict, List, Union, TypeAlias, Set, Tuple

Config : TypeAlias = Dict[str, Any] # TODO: Import Config class when it is defined


class Param:
    """
    Define a parameter with properties and constraints for runtime validation.

    Attributes
    ----------
    value : Any
        Value set at runtime.
    default : Any
        Default value for the parameter.
    param_type : Optional[type]
        Type of the parameter value. This should be a built-in Python type or a custom class.
    validator : Optional[Callable[[Any], bool]]
        Function to validate the parameter value.
    regex : Optional[str]
        Regular expression pattern to match the parameter value.

    Methods
    -------
    validate(value: Any) -> bool
        Validate parameter against the provided constraints.
    set_value(value: Any)
        Set and validate parameter value at runtime.
    get_value() -> Any
        Retrieve the set value or default.

    Examples
    --------
    Define a parameter with a default value and a validator:

    >>> def is_positive(value: Any) -> bool:
    ...     return value > 0
    >>>
    >>> param = Param(default=42, validator=is_positive)

    Set a value for the parameter:

    >>> param.set_value(7)
    >>> param.get_value()
    7

    Validate against a regex pattern:

    >>> param = Param(regex=r'^[A-Z]{3}$')
    >>> param.set_value('ABC')
    >>> param.get_value()
    'ABC'
    """
    def __init__(
        self,
        default: Any = None,
        param_type: Optional[type] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        options: Optional[Set[Any]] = None,
        regex: Optional[str] = None,
        validators: Union[Callable[[Any], bool], Iterable[Callable[[Any], bool]]] = None, # TODO: allow more general container types than list
        strict: bool = True
    ):
        self.value = None  # set at runtime
        self.default = default
        self.param_type = param_type
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.regex = regex
        self.options = set(options) if options else None
        self.validators = (
            [validators] if callable(validators)
            else list(validators) if isinstance(validators, Iterable)
            else []
        )
        self.strict = strict

    def validate(self, value: Any) -> bool:
        """
        Validate a candidate value against the provided constraints.

        Arguments
        ---------
        value : Any
            Value to validate.

        Returns
        -------
        valid : bool
            True if the value is valid, False otherwise.

        Raises
        ------
        TypeError
            If the value does not match the expected type.
        ValueError
            If the value does not match the constraints.
        """
        if self.param_type and not isinstance(value, self.param_type):
            raise TypeError(f"Expected type {self.param_type}, got {type(value)}.")
        if self.gt is not None and not value > self.gt:
            raise ValueError(f"Parameter value {value} must be greater than {self.gt}")
        if self.ge is not None and not value >= self.ge:
            raise ValueError(f"Parameter value {value} must be greater than or equal to {self.ge}")
        if self.lt is not None and not value < self.lt:
            raise ValueError(f"Parameter value {value} must be less than {self.lt}")
        if self.le is not None and not value <= self.le:
            raise ValueError(f"Parameter value {value} must be less than or equal to {self.le}")
        if self.regex and not re.match(self.regex, str(value)):
            raise ValueError(f"Parameter value {value} does not match the regex pattern {self.regex}.")
        if self.options and value not in self.options:
            raise ValueError(f"Parameter value {value} is not in allowed options: {self.options}.")
        for validator in self.validators:
            if not validator(value):
                raise ValueError(f"Parameter value {value} does not pass the validation constraint {validator}.")
        return True

    def set_value(self, value: Any) -> None:
        """Set a value at runtime, if valid."""
        if self.strict:
            self.validate(value)
        self.value = value

    def get_value(self) -> Any:
        """Retrieve the value (if set) or its default (None if not specified)."""
        if self.value is not None:
            return self.value
        return self.default

    def add_validator(self, validator: Callable[[Any], bool]):
        """Add a validator to the parameter."""
        self.validators.append(validator)


class SweepParam(Param):
    """
    Define a parameter for a parameter sweep.

    Attributes
    ----------
    values : List[Any]
        List of values for the parameter sweep.

    Methods
    -------
    get_values() -> List[Any]
        Retrieve the values for the parameter sweep.

    Examples
    --------
    Define a parameter for a parameter sweep:

    >>> param = SweepParam(values=[1, 2, 3])

    Retrieve the values for the parameter sweep:

    >>> param.get_values()
    [1, 2, 3]
    """
    def __init__(self, values: List[Any], **kwargs):
        super().__init__(**kwargs)
        self.values = values

    def get_values(self) -> List[Any]:
        """Retrieve the values for the parameter sweep."""
        return self.values

    def validate(self) -> bool:
        """Override the validate method to perform validation over all the values."""
        return all(super().validate(value) for value in self.values)


class ParameterSet(UserDict[str, Param]):
    """
    Manage a collection of parameters.

    Attributes
    ----------
    data : Dict[str, Param]
        Underlying dictionary of parameters, inheriting from UserDict.

    Methods
    -------
    get(key: str) -> Param
        Retrieve a parameter by name.
    override(**overrides) -> ParameterSet
        Create a new parameter set with modifications.
    apply_config(config: Dict[str, Any])
        Apply runtime configuration values to the parameters.

    Examples
    --------
    Create a parameter set with two parameters:

    >>> params = ParameterSet(
    ...     param1=Param(default=42, min_value=0),
    ...     param2=Param(param_type=str, regex=r'^[A-Z]{3}$')
    ... )

    Retrieve a parameter by name:

    >>> params.get('param1')
    Param(default=42)

    Override a parameter:

    >>> new_params = params.override(param1=Param(default=7))
    >>> new_params.get('param1')

    Apply a configuration to the parameters:

    >>> config = {'param1': 7, 'param2': 'bar'}
    >>> params.apply_config(config)
    >>> params.get('param1')
    7

    Notes
    -----
    All the methods of the UserDict class are available for this object, and by extension all the
    dict methods. The main difference is that the values are Param objects, which provide additional
    validation and constraints.

    The `add`, `remove` and `override` methods provide flexibility to enable hierarchical
    construction of parameter sets for different workflows, from the most general to the most
    specific. This mirrors the hierarchical configurations of the YAML files.

    See Also
    --------
    Param
        Custom parameter class with validation constraints.
    collections.UserDict
        Inherit from this class to create a dictionary-like object.
    """
    def __init__(self, *args, strict: bool = True, **kwargs):
        """
        Initialize parameters from a dictionary or keyword arguments.

        Arguments
        ---------
        *args : Tuple
            Positional arguments to initialize the parameter set.
            Used to pass a dictionary as the first argument.
        strict : bool
            Flag to enable strict validation mode. Its value will be propagated to all parameters.
        **kwargs : Dict[str, Param]
            Keyword arguments to initialize the parameter set.
            Used to pass parameters directly as keyword arguments.
            If the values are not Param objects, they will be converted to Param objects and the
            provided value will serve as the 'default' attribute of the Param object.

        Examples
        --------
        Initialize parameters from a dictionary:

        >>> params = ParameterSet({'param1': Param(default=42), 'param2': Param(default='foo')})

        Initialize parameters from keyword arguments:

        >>> params = ParameterSet(param1=Param(default=42), param2=Param(default='foo'))

        Notes
        -----
        The `global_validators` attribute cannot be set at initialization and must be set manually
        after the parameter set is created. This choice clarifies the specification of the global
        validators in a separate step.

        Implementation
        --------------
        Choice of the candidate set to pass to the constructor:

        - If the first argument is a dictionary, use it as the candidate set.
        - If the first argument is not a dictionary, use the keyword arguments.

        The `global_validators` attribute is type hinted as a list of tuples, where each tuple
        contains a validator function and a target specification. This type is preferred to a
        dictionary with functions as keys, in order to facilitate serialization.
        """
        super().__init__() # initialize with the parent class constructor (UserDict)
        self.strict = strict
        candidates = args[0] if args and isinstance(args[0], dict) else kwargs
        self.data.update({k: self.convert(v) for k, v in candidates.items()})
        self.global_validators: List[Tuple] = []

    def convert(self, value: Any) -> Param:
        """
        Ensure that the value is a Param object and set the strict mode.

        Arguments
        ---------
        value : Any
            Value to convert to a Param object. It will be used as the default value.
        """
        if isinstance(value, Param): # enforce same strict mode as the parent
            value.strict = self.strict
            return value
        else: # convert to Param object with the provided value as the default
            return Param(default=value, strict=self.strict)

    def __setitem__(self, key: str, value: Any) -> None:
        """Override the `__setitem__` method to ensure that the value is a Param object."""
        self.data[key] = self.convert(value)

    def __getattr__(self, name: str) -> Any:
        """
        Access nested parameters using dot notation.

        Overrides the `__getattr__` method to access the nested value of the parameters as if they
        were attributes of the ParameterSet object. It supports arbitrary levels of nesting and
        works with both direct parameters and nested ParameterSets.

        Parameters
        ----------
        name : str
            Attribute name to access, which may include dots for nested access (e.g.
            'model.layers.hidden_units').

        Returns
        -------
        Any
            Value of the parameter, if found.

        Raises
        ------
        AttributeError
            If the specified parameter is not found in the ParameterSet.

        Implementation
        --------------
        1. Split the attribute name by dots to obtain a list of keys.
        2. Iteratively traverse the nested structure using these keys.
        3. If a Param object is encountered, return its value.
        4. If a nested ParameterSet is encountered, continue traversing.
        5. If the traversal completes without finding a Param, return the final object (since the
           query might be for a nested ParameterSet).
        6. If any key is not found during traversal, fall back to standard attribute access.

        Example
        -------
        Define a nested parameter set and access its values using dot notation:

        >>> nested_params = ParameterSet(
        ...     model=ParameterSet(
        ...         learning_rate=Param(default=0.01),
        ...         layers=ParameterSet(
        ...             hidden_units=Param(default=128)
        ...         )
        ...     )
        ... )
        >>> print(nested_params.model.learning_rate)
        0.01
        >>> print(nested_params.model.layers.hidden_units)
        128
        >>> print(nested_params.non_existent)
        AttributeError: No parameter 'non_existent' in the ParameterSet.
        """
        keys = name.split(".") # split the attribute name by dots
        obj = self # start traversal from the current object
        try:
            for key in keys:
                if isinstance(obj, ParameterSet) and key in obj.data:
                    obj = obj.data[key] # update the object to the nested ParameterSet
                    if isinstance(obj, Param): # hit a Param object -> successful query
                        return obj.get_value()
                else: # delegate to parent class
                    return super().__getattr__(name)
            return obj # end of traversal without error -> query for the final object
        except AttributeError: # if AttributeError at any point, stop traversal
            return super().__getattr__(name) # delegate to parent class

    def add(self, name: str, param: Param):
        """Add a new parameter."""
        self.data[name] =  self.convert(param)

    def remove(self, name: str):
        """Remove a parameter."""
        self.data.pop(name, None)

    def override(self, **overrides) -> Self:
        """Create a modified copy of the parameter set."""
        new_set = ParameterSet(self.data.copy())
        new_set.update(overrides)
        return new_set

    def add_validator(self, target: str, validator: Callable[[Any], bool]):
        """
        Register a validator to a specific parameter.

        Arguments
        ---------
        target : str
            Name of the parameter targeted by the validator.
        validator : Callable[[Any], bool]
            Function to validate the parameter value. It must take a single argument and return a
            bool.

        Examples
        --------
        Add a validator to a parameter:

        >>> params = ParameterSet(param1=Param(default=42))
        >>> def is_positive(value: Any) -> bool:
        ...     return value > 0
        >>> params.add_validator('param1', is_positive)
        """
        if target in self.data:
            self.data[target].add_validator(validator)
        else:
            raise AttributeError(f"No parameter '{target}' in the ParameterSet.")

    def add_global_validator(self, validator, targets):
        """
        Register a global validator function that tests relationships between parameters.

        Arguments
        ---------
        validator :
            Function that takes several values and returns a boolean.
        targets : List[str] or Dict[str, str]
            Parameter specification to extract the parameters that this validator applies to.
            If list, it contains the names of the parameters to pass as positional arguments.
            If dict, it contains the names of the parameters to pass as keyword arguments. The keys
            are the names of the function's arguments, and the values are the names of the
            parameters in the ParameterSet.

        Examples
        --------
        Define a global validator that checks if one parameter is greater than another:

        >>> def is_greater_than(x, y):
        ...     return x > y

        Add the global validator (pass parameters as positional arguments internally):

        >>> params = ParameterSet(param1=Param(default=1), param2=Param(default=2))
        >>> params.add_global_validator(is_greater_than, params=['param1', 'param2'])
        >>> params.validate()
        >>> # internal call: is_greater_than(params.param1, params.param2)
        True

        Add the global validator (pass parameters as keyword arguments internally):

        >>> params.add_global_validator(is_greater_than, params={'x': 'param1', 'y': 'param2'})
        >>> params.validate()
        >>> # internal call: is_greater_than(x=params.param1, y=params.param2)
        True
        """
        self.global_validators.append((validator, targets))

    def apply_config(self, config: Config) -> None:
        """
        Apply runtime configuration values to the parameters.

        Arguments
        ---------
        config : Config
            Configuration values to apply.

        Notes
        -----
        Parameters are set by filtering the configuration objects and retrieving the values for the
        relevant keys which match the parameter names.
        The parameter lookup is performed by screening the key within the ParameterSet object rather
        than the configuration object, since the latter might contain many irrelevant items.

        WHen a parameter is matched, its value is set in the Param object using the `set_value`
        method, which performs broadcast validation on the value.
        """
        for key, param in self.data.items():
            if key in config.values:
                param.set_value(config.get(key))

    def validate(self) -> bool:
        """
        Validate all parameters in the set.

        1. Check individual parameters for type and constraints.
        2. Check global validators for relationships between parameters.

        Returns
        -------
        valid : bool
            True if all parameters are valid, False otherwise.
        """
        # Validate individual parameters
        for param in self.data.values():
            try:
                param.validate(param.get_value())
            except (TypeError, ValueError) as e:
                print(f"Validation error in {self.__class__.__name__}: {e}")
        # Validate global constraints
        for validator, targets in self.global_validators: # access tuples of (validator, targets)
            # extract the values from the ParameterSet
            if isinstance(targets, list):
                values = [self.data[t].get_value() for t in targets]
                outcome = validator(*values) # pass as positional arguments
            elif isinstance(targets, dict):
                values = {k: self.data[v].get_value() for k, v in targets.items()}
                outcome = validator(**values) # pass as keyword arguments
            if not outcome:
                raise ValueError(f"Global validation failed for {validator.__name__}")

    def generate_sweep_grid(self) -> List[Dict[str, Any]]:
        """
        Generate a list of configurations for parameter sweeps.

        Returns
        -------
        grid : List[Dict[str, Any]]
            List of configuration dictionaries.
        """
        sweep_params = {k: v.get_values() for k, v in self.data.items() if isinstance(v, SweepParam)}
        static_params = {k: v.get_value() for k, v in self.data.items() if not isinstance(v, SweepParam)}
        sweep_keys, sweep_values = zip(*sweep_params.items())
        grid = []
        for combination in product(*sweep_values):
            config = static_params.copy()
            config.update(dict(zip(sweep_keys, combination)))
            grid.append(config)
        return grid

    def merge(self, other: Self, override: bool = False) -> Self:
        """
        Merge two parameter sets.

        Arguments
        ---------
        other : ParameterSet
            Parameter set to merge with.
        override : bool
            If True, override existing parameters with new values.

        Returns
        -------
        merged : ParameterSet
            Merged parameter set.
        """
        merged = ParameterSet(self.data.copy())
        for key, value in other.data.items():
            if key not in merged.data or override:
                merged.data[key] = value
        return merged
