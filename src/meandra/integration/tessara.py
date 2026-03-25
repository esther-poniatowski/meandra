"""
meandra.integration.tessara
===========================

Integration adapters for Tessara parameter management.

Classes
-------
TessaraNodeAdapter
    Adapts Tessara parameters for injection into Meandra nodes.
SweepOrchestrator
    Executes workflows across all parameter combinations from a ParamSweeper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Callable, Iterable, Tuple
from functools import wraps
import logging
import copy

if TYPE_CHECKING:
    from tessara import ParameterSet, ParamSweeper
    from meandra.core.node import Node
    from meandra.core.workflow import Workflow
    from meandra.orchestration.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class TessaraNodeAdapter:
    """
    Adapts Tessara parameters for injection into Meandra nodes.

    This adapter bridges the gap between Tessara's parameter management
    and Meandra's workflow execution by:
    - Injecting validated parameters into node functions
    - Creating parameter-aware node wrappers
    - Supporting both explicit parameter binding and automatic discovery

    Attributes
    ----------
    params : ParameterSet
        The Tessara parameter set to inject into nodes.

    Examples
    --------
    Basic usage with a node function:

    >>> from tessara import ParameterSet, Param
    >>> params = ParameterSet(lr=Param(default=0.01), epochs=Param(default=100))
    >>> adapter = TessaraNodeAdapter(params)
    >>>
    >>> def train(inputs, lr, epochs):
    ...     return {"model": f"trained with lr={lr}, epochs={epochs}"}
    >>>
    >>> wrapped = adapter.wrap_function(train)
    >>> result = wrapped({"data": [1, 2, 3]})
    """

    def __init__(self, params: "ParameterSet", validate: bool = False) -> None:
        """
        Initialize the adapter with a parameter set.

        Parameters
        ----------
        params : ParameterSet
            Tessara parameter set containing parameters to inject.
        """
        self.params = params
        self.validate = validate

    def iter_params(self) -> Iterable[Tuple[str, Any]]:
        """
        Iterate over parameters with dotted paths.

        Returns tuples of (path, Param-like object).
        """
        return self._iter_params(self.params)

    def _iter_params(
        self,
        param_set: "ParameterSet",
        prefix: Tuple[str, ...] = (),
    ) -> Generator[Tuple[str, Any], None, None]:
        for key, value in param_set.data.items():
            if hasattr(value, "data"):
                yield from self._iter_params(value, prefix + (key,))
            else:
                path = ".".join(prefix + (key,))
                yield path, value

    def get_param_values(self, names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract parameter values from the parameter set.

        Parameters
        ----------
        names : List[str], optional
            Specific parameter names to extract. If None, extracts all.

        Returns
        -------
        Dict[str, Any]
            Dictionary mapping parameter names to their current values.
        """
        if names is None:
            return self.params.to_dict(values_only=True)

        # Build lookup map once for all nested and top-level params
        param_map = dict(self.iter_params())

        # Also include top-level non-nested params by their simple names
        for key, value in self.params.data.items():
            if not hasattr(value, "data") and key not in param_map:
                param_map[key] = value

        result = {}
        for name in names:
            if name in param_map:
                param_obj = param_map[name]
                result[name] = param_obj.get() if hasattr(param_obj, "get") else param_obj
            elif "." in name:
                # Fallback for dotted paths not in iter_params (e.g., dynamic access)
                result[name] = self.params.get_value(name)
        return result

    def _validate_param_values(self, names: List[str]) -> None:
        if not self.validate:
            return
        param_map = dict(self.iter_params())
        for name in names:
            if name not in param_map:
                continue
            param_obj = param_map[name]
            if hasattr(param_obj, "get") and hasattr(param_obj, "validate_value"):
                value = param_obj.get()
                param_obj.validate_value(value)

    def wrap_function(
        self,
        func: Callable[..., Any],
        param_names: Optional[List[str]] = None,
        param_aliases: Optional[Dict[str, str]] = None,
        validate: Optional[bool] = None,
    ) -> Callable[[Dict[str, Any]], Any]:
        """
        Wrap a function to inject parameters from the parameter set.

        Parameters
        ----------
        func : Callable
            Function to wrap. Should accept inputs dict plus parameter kwargs.
        param_names : List[str], optional
            Specific parameters to inject. If None, injects all matching
            function signature parameters.

        Returns
        -------
        Callable[[Dict[str, Any]], Any]
            Wrapped function that receives only inputs dict.

        Examples
        --------
        >>> def process(inputs, threshold=0.5):
        ...     return {"filtered": [x for x in inputs["data"] if x > threshold]}
        >>>
        >>> params = ParameterSet(threshold=Param(default=0.7))
        >>> adapter = TessaraNodeAdapter(params)
        >>> wrapped = adapter.wrap_function(process)
        >>> wrapped({"data": [0.3, 0.8, 0.6]})
        {'filtered': [0.8]}
        """
        import inspect

        sig = inspect.signature(func)
        func_params = set(sig.parameters.keys()) - {"inputs"}
        has_var_kwargs = any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in sig.parameters.values()
        )
        param_aliases = param_aliases or {}

        if param_names is None:
            # Auto-discover: inject parameters matching function signature
            inject_names = []
            if has_var_kwargs:
                inject_names = [name for name, _ in self.iter_params()]
                for name in self.params.data.keys():
                    if name not in inject_names and not hasattr(self.params.data[name], "data"):
                        inject_names.append(name)
            else:
                for name, _ in self.iter_params():
                    if name in func_params:
                        inject_names.append(name)
                    else:
                        alias = param_aliases.get(name)
                        if alias in func_params:
                            inject_names.append(name)
                for name in self.params.data.keys():
                    if name in func_params and name not in inject_names:
                        inject_names.append(name)
        else:
            inject_names = param_names

        @wraps(func)
        def wrapped(inputs: Dict[str, Any]) -> Any:
            do_validate = self.validate if validate is None else validate
            if do_validate:
                self._validate_param_values(inject_names)
            param_values = self.get_param_values(inject_names)
            if param_aliases:
                param_values = {
                    param_aliases.get(name, name): value
                    for name, value in param_values.items()
                }
            return func(inputs, **param_values)

        return wrapped

    def bind_to_node(
        self,
        node: "Node",
        param_names: Optional[List[str]] = None,
        param_aliases: Optional[Dict[str, str]] = None,
        validate: Optional[bool] = None,
    ) -> "Node":
        """
        Create a new node with parameters injected into its function.

        Parameters
        ----------
        node : Node
            The node to adapt.
        param_names : List[str], optional
            Specific parameters to inject. If None, auto-discovers from
            function signature.

        Returns
        -------
        Node
            New node with parameter-injected function.
        """
        wrapped_func = self.wrap_function(node.func, param_names, param_aliases, validate)
        return node.clone(func=wrapped_func)

    def adapt_workflow(
        self,
        workflow: "Workflow",
        node_params: Optional[Dict[str, List[str]]] = None,
        node_aliases: Optional[Dict[str, Dict[str, str]]] = None,
        validate: Optional[bool] = None,
    ) -> "Workflow":
        """
        Create a new workflow with parameters injected into specified nodes.

        Parameters
        ----------
        workflow : Workflow
            The workflow to adapt.
        node_params : Dict[str, List[str]], optional
            Mapping of node names to parameter names to inject.
            If None, auto-discovers for all nodes.

        Returns
        -------
        Workflow
            New workflow with parameter-adapted nodes.
        """
        def transform(node: "Node") -> "Node":
            if node_params is None or node.name in node_params:
                params_for_node = node_params.get(node.name) if node_params else None
                aliases_for_node = node_aliases.get(node.name) if node_aliases else None
                return self.bind_to_node(node, params_for_node, aliases_for_node, validate)
            return node

        return workflow.transform_nodes(transform)

    def transform_node(self, node: "Node") -> "Node":
        """Implement the stable node-transformer seam."""
        return self.bind_to_node(node)

    def transform_workflow(self, workflow: "Workflow") -> "Workflow":
        """Implement the stable workflow-transformer seam."""
        return self.adapt_workflow(workflow)


class SweepOrchestrator:
    """
    Execute a workflow for each parameter combination from a ParamSweeper.

    Automates running the same workflow multiple times with different
    parameter configurations, collecting results from all runs.

    Attributes
    ----------
    orchestrator : Orchestrator
        The underlying orchestrator for workflow execution.
    sweeper : ParamSweeper
        Tessara parameter sweeper providing combinations.

    Examples
    --------
    >>> from tessara import ParameterSet, Param, ParamGrid, ParamSweeper
    >>> params = ParameterSet(
    ...     lr=ParamGrid(Param(), sweep_values=[0.01, 0.001]),
    ...     epochs=Param(default=100),
    ... )
    >>> sweeper = ParamSweeper(params)
    >>> sweep_orch = SweepOrchestrator(orchestrator, sweeper)
    >>> results = sweep_orch.run_sweep(workflow, inputs)
    >>> len(results)  # 2 runs for 2 lr values
    2
    """

    def __init__(
        self,
        orchestrator: "Orchestrator",
        sweeper: "ParamSweeper",
    ) -> None:
        """
        Initialize the sweep orchestrator.

        Parameters
        ----------
        orchestrator : Orchestrator
            Meandra orchestrator for workflow execution.
        sweeper : ParamSweeper
            Tessara parameter sweeper for generating combinations.
        """
        self.orchestrator = orchestrator
        self.sweeper = sweeper

    def run_sweep(
        self,
        workflow: "Workflow",
        inputs: Optional[Dict[str, Any]] = None,
        node_params: Optional[Dict[str, List[str]]] = None,
        on_run_complete: Optional[Callable[[int, Dict[str, Any], Dict[str, Any]], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute the workflow for all parameter combinations.

        Parameters
        ----------
        workflow : Workflow
            The workflow to execute.
        inputs : Dict[str, Any], optional
            Initial inputs for the workflow.
        node_params : Dict[str, List[str]], optional
            Mapping of node names to parameter names for injection.
        on_run_complete : Callable, optional
            Callback called after each run with (index, params_dict, results).

        Returns
        -------
        List[Dict[str, Any]]
            List of results from each parameter combination run.
            Each dict contains:
            - 'params': The parameter values used
            - 'outputs': The workflow outputs
            - 'success': Whether the run completed successfully
            - 'error': Error message if failed (only if success=False)
        """
        inputs = inputs or {}
        results = []

        for idx, param_set in enumerate(self.sweeper):
            param_dict = param_set.to_dict(values_only=True)
            total = None
            try:
                total = len(self.sweeper)
            except TypeError:
                total = None
            if total is not None:
                logger.info(f"Sweep run {idx + 1}/{total}: {param_dict}")
            else:
                logger.info(f"Sweep run {idx + 1}: {param_dict}")

            adapter = TessaraNodeAdapter(param_set, validate=True)
            adapted_workflow = adapter.adapt_workflow(workflow, node_params)

            try:
                outputs = self.orchestrator.run(adapted_workflow, copy.deepcopy(inputs))
                run_result = {
                    "params": param_dict,
                    "outputs": outputs,
                    "success": True,
                }
            except Exception as e:
                logger.error(f"Sweep run {idx + 1} failed: {e}")
                run_result = {
                    "params": param_dict,
                    "outputs": {},
                    "success": False,
                    "error": str(e),
                }

            results.append(run_result)

            if on_run_complete:
                on_run_complete(idx, param_dict, run_result)

        return results

    def __len__(self) -> int:
        """Return the total number of parameter combinations."""
        return len(self.sweeper)
