"""
meandra.orchestration.orchestrator
==================================

Workflow execution orchestration.
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4
import logging
import inspect

from meandra.core.workflow import Workflow
from meandra.core.node import Node
from meandra.scheduling.scheduler import Scheduler, DAGScheduler
from meandra.monitoring.state_tracker import StateTracker, InMemoryStateTracker
from meandra.checkpoint.manager import CheckpointManager
from meandra.configuration.mod import ConfigProvider
from meandra.logging.context import LogContextManager
from meandra.monitoring.progress import ProgressTracker
from meandra.monitoring.retry import RetryConfig, execute_with_retry
from meandra.core.errors import (
    NodeExecutionError,
    DependencyResolutionError,
    ValidationError as WorkflowValidationError,
)


logger = logging.getLogger(__name__)


class HookEvent(str, Enum):
    """Lifecycle events for workflow execution."""

    BEFORE_WORKFLOW = "before_workflow"
    AFTER_WORKFLOW = "after_workflow"
    BEFORE_NODE = "before_node"
    AFTER_NODE = "after_node"
    ON_ERROR = "on_error"


# Type aliases for hook callbacks
BeforeWorkflowHook = Callable[[Workflow, Dict[str, Any]], None]
AfterWorkflowHook = Callable[[Workflow, Dict[str, Any], Dict[str, Any]], None]
BeforeNodeHook = Callable[[Node, Dict[str, Any]], None]
AfterNodeHook = Callable[[Node, Dict[str, Any], Dict[str, Any]], None]
OnErrorHook = Callable[[Node, Exception, Dict[str, Any]], None]


class WorkflowExecutionError(NodeExecutionError):
    """Raised when workflow execution fails."""

    def __init__(
        self,
        message: str,
        workflow_name: str,
        node_name: str,
        original_error: Exception,
    ):
        super().__init__(
            message,
            workflow_name=workflow_name,
            node_name=node_name,
            original_error=original_error,
        )


class Orchestrator(ABC):
    """
    Abstract base class for workflow execution.

    An orchestrator controls how a workflow is executed, managing
    node ordering, input/output flow, and error handling.
    """

    @abstractmethod
    def run(self, workflow: Workflow, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with given inputs.

        Parameters
        ----------
        workflow : Workflow
            The workflow to execute.
        inputs : Dict[str, Any]
            Initial inputs for the workflow.

        Returns
        -------
        Dict[str, Any]
            All outputs from all nodes.
        """
        pass


class SchedulingOrchestrator(Orchestrator):
    """
    Execute workflows using a scheduler for dependency resolution.

    Resolves node dependencies, executes nodes in valid order,
    and manages the flow of data between nodes.

    Attributes
    ----------
    scheduler : Scheduler
        Scheduler for resolving execution order.
    state_tracker : Optional[StateTracker]
        Tracker for monitoring execution state.
    fail_fast : bool
        If True, stop on first failure. If False, continue with
        nodes that don't depend on failed nodes.

    Examples
    --------
    >>> orchestrator = SchedulingOrchestrator()
    >>> results = orchestrator.run(workflow, {"input_data": data})

    With custom scheduler:

    >>> scheduler = DAGScheduler()
    >>> orchestrator = SchedulingOrchestrator(scheduler=scheduler, fail_fast=False)
    """

    def __init__(
        self,
        scheduler: Optional[Scheduler] = None,
        state_tracker: Optional[StateTracker] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
        progress_tracker: Optional[ProgressTracker] = None,
        retry_config: Optional[RetryConfig] = None,
        fail_fast: bool = True,
        resume_from_checkpoint: bool = True,
        max_workers: Optional[int] = None,
    ):
        """
        Initialize the orchestrator.

        Parameters
        ----------
        scheduler : Optional[Scheduler]
            Scheduler for resolving execution order. Defaults to DAGScheduler.
        state_tracker : Optional[StateTracker]
            Tracker for monitoring execution state.
        checkpoint_manager : Optional[CheckpointManager]
            Manager for checkpointing node outputs.
        fail_fast : bool
            If True, stop on first failure. If False, continue with
            nodes that don't depend on failed nodes.
        resume_from_checkpoint : bool
            If True and checkpoint_manager is set, resume from last checkpoint.
        max_workers : Optional[int]
            Maximum number of parallel workers for executing nodes within
            a layer. If None (default), nodes are executed sequentially.
            Set to a positive integer to enable parallel execution.
        """
        self.scheduler = scheduler or DAGScheduler()
        self._state_tracker = state_tracker
        self._checkpoint_manager = checkpoint_manager
        self._progress_tracker = progress_tracker
        self._retry_config = retry_config
        self.fail_fast = fail_fast
        self.resume_from_checkpoint = resume_from_checkpoint
        self.max_workers = max_workers
        self._hooks: Dict[HookEvent, List[Callable[..., Any]]] = {
            event: [] for event in HookEvent
        }

    def add_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        """
        Register a callback for a lifecycle event.

        Parameters
        ----------
        event : HookEvent
            The event to hook into.
        callback : Callable
            Function to call when the event occurs.

            Callback signatures by event:
            - BEFORE_WORKFLOW: (workflow, inputs) -> None
            - AFTER_WORKFLOW: (workflow, inputs, outputs) -> None
            - BEFORE_NODE: (node, inputs) -> None
            - AFTER_NODE: (node, inputs, outputs) -> None
            - ON_ERROR: (node, exception, context) -> None

        Examples
        --------
        >>> def log_node_start(node, inputs):
        ...     print(f"Starting {node.name}")
        >>> orchestrator.add_hook(HookEvent.BEFORE_NODE, log_node_start)
        """
        self._validate_hook_signature(event, callback)
        self._hooks[event].append(callback)

    def remove_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        """
        Remove a registered callback.

        Parameters
        ----------
        event : HookEvent
            The event the callback was registered for.
        callback : Callable
            The callback to remove.
        """
        if callback in self._hooks[event]:
            self._hooks[event].remove(callback)

    def _emit(self, event: HookEvent, *args: Any) -> None:
        """Emit an event to all registered hooks."""
        for callback in self._hooks[event]:
            try:
                callback(*args)
            except Exception as e:
                logger.warning(f"Hook callback failed for {event}: {e}")

    def _validate_hook_signature(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        """Validate hook callback signature against expected parameters."""
        expected_args = {
            HookEvent.BEFORE_WORKFLOW: 2,
            HookEvent.AFTER_WORKFLOW: 3,
            HookEvent.BEFORE_NODE: 2,
            HookEvent.AFTER_NODE: 3,
            HookEvent.ON_ERROR: 3,
        }
        required = expected_args[event]
        try:
            inspect.signature(callback).bind_partial(*([object()] * required))
        except TypeError as exc:
            raise ValueError(
                f"Hook callback for {event.value} must accept {required} positional arguments"
            ) from exc

    def run(self, workflow: Workflow, inputs: Dict[str, Any] | ConfigProvider) -> Dict[str, Any]:
        """
        Execute a workflow with given inputs.

        Parameters
        ----------
        workflow : Workflow
            The workflow to execute.
        inputs : Dict[str, Any]
            Initial inputs for the workflow.

        Returns
        -------
        Dict[str, Any]
            All outputs from all nodes, merged into a single dict.

        Raises
        ------
        WorkflowExecutionError
            If a node fails and fail_fast is True.
        """
        run_id = str(uuid4())[:8]
        state_tracker = self._state_tracker or InMemoryStateTracker(
            workflow.name, run_id
        )

        logger.info(f"Starting workflow '{workflow.name}' (run_id={run_id})")

        # Resolve inputs from config provider if needed
        if isinstance(inputs, ConfigProvider):
            inputs.resolve()
            inputs_dict = inputs.to_dict()
        else:
            inputs_dict = dict(inputs)

        with LogContextManager(run_id=run_id, workflow_name=workflow.name):
            # Emit before_workflow hook
            self._emit(HookEvent.BEFORE_WORKFLOW, workflow, inputs_dict)

            # Get execution layers
            try:
                layers = self.scheduler.resolve(workflow)
            except Exception as exc:
                raise DependencyResolutionError(
                    str(exc),
                    workflow_name=workflow.name,
                ) from exc

            # Context holds all outputs from all nodes
            context: Dict[str, Any] = dict(inputs_dict)
            failed_nodes: set[str] = set()

            # Track completed node names for checkpoint resumption
            completed_nodes: set[str] = set()
            if self._checkpoint_manager and self.resume_from_checkpoint:
                checkpoint = self._checkpoint_manager.load_latest(workflow.name)
                if checkpoint:
                    workflow_hash = workflow.structure_hash()
                    if checkpoint.info.workflow_hash and checkpoint.info.workflow_hash != workflow_hash:
                        logger.warning(
                            "Checkpoint workflow hash mismatch for '%s': %s != %s",
                            workflow.name,
                            checkpoint.info.workflow_hash,
                            workflow_hash,
                        )
                    context.update(checkpoint.context)
                    # Mark all nodes up to checkpoint as completed
                    execution_order = [node for layer in layers for node in layer]
                    for i, node in enumerate(execution_order):
                        if i <= checkpoint.info.node_index:
                            completed_nodes.add(node.name)

            # Track global node index for checkpointing
            node_index = 0

            if self._progress_tracker is not None:
                self._progress_tracker.total_nodes = len(workflow)

            for layer in layers:
                # Execute layer (parallel or sequential)
                layer_results = self._execute_layer(
                    layer=layer,
                    workflow=workflow,
                    context=context,
                    state_tracker=state_tracker,
                    failed_nodes=failed_nodes,
                    completed_nodes=completed_nodes,
                    run_id=run_id,
                    start_node_index=node_index,
                )

                # Update context with layer results
                context.update(layer_results)
                node_index += len(layer)

            # Emit after_workflow hook
            self._emit(HookEvent.AFTER_WORKFLOW, workflow, inputs_dict, context)

            if self._progress_tracker is not None:
                self._progress_tracker.finish()

            logger.info(f"Workflow '{workflow.name}' completed (run_id={run_id})")
            return context

    def _execute_node(
        self,
        node: Node,
        workflow: Workflow,
        context: Dict[str, Any],
        state_tracker: StateTracker,
        node_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a single node.

        Parameters
        ----------
        node : Node
            The node to execute.
        workflow : Workflow
            The workflow containing the node.
        context : Dict[str, Any]
            Current execution context with all available data.
        state_tracker : StateTracker
            State tracker for logging.
        node_inputs : Optional[Dict[str, Any]]
            Pre-gathered inputs for the node. If None, will be gathered.

        Returns
        -------
        Dict[str, Any]
            Node outputs.
        """
        state_tracker.mark_running(node.name)

        # Gather inputs if not provided
        if node_inputs is None:
            node_inputs = self._gather_inputs(node, workflow, context)

        # Execute
        if self._retry_config is not None:
            outputs = execute_with_retry(
                node.execute,
                self._retry_config,
                None,
                node_inputs,
            )
        else:
            outputs = node.execute(node_inputs)

        state_tracker.mark_completed(node.name, outputs)
        return outputs

    def _gather_inputs(
        self,
        node: Node,
        workflow: Workflow,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Gather inputs for a node from the execution context.

        Parameters
        ----------
        node : Node
            The node needing inputs.
        context : Dict[str, Any]
            Current execution context.

        Returns
        -------
        Dict[str, Any]
            Inputs for the node.
        """
        # If node specifies explicit inputs, use those
        if node.inputs:
            missing = [key for key in node.inputs if key not in context]
            if missing:
                raise KeyError(f"Missing inputs for node '{node.name}': {missing}")
            return {key: context[key] for key in node.inputs}

        # If node accepts full context, return it
        if node.accepts_context:
            return context

        # Otherwise, infer inputs from dependency outputs
        if node.dependencies:
            inferred: Dict[str, Any] = {}
            for dep_name in node.dependencies:
                dep = workflow.get_node(dep_name)
                for out_key in dep.outputs:
                    if out_key in context:
                        inferred[out_key] = context[out_key]
            if not inferred:
                raise KeyError(
                    f"Node '{node.name}' has no explicit inputs and no dependency outputs"
                )
            return inferred

        # Source node with no inputs
        if not node.inputs and not node.dependencies:
            return {}

        raise KeyError(f"Node '{node.name}' requires explicit inputs or accepts_context=True")

    def _execute_layer(
        self,
        layer: List[Node],
        workflow: Workflow,
        context: Dict[str, Any],
        state_tracker: StateTracker,
        failed_nodes: set[str],
        completed_nodes: set[str],
        run_id: str,
        start_node_index: int,
    ) -> Dict[str, Any]:
        """
        Execute all nodes in a layer.

        If max_workers is set, nodes are executed in parallel.
        Otherwise, nodes are executed sequentially.

        Parameters
        ----------
        layer : List[Node]
            Nodes in this execution layer.
        workflow : Workflow
            The workflow being executed.
        context : Dict[str, Any]
            Current execution context.
        state_tracker : StateTracker
            State tracker for logging.
        failed_nodes : set[str]
            Set of failed node names (updated in place).
        completed_nodes : set[str]
            Set of already completed node names.
        run_id : str
            Current run identifier.
        start_node_index : int
            Starting index for nodes in this layer.

        Returns
        -------
        Dict[str, Any]
            Combined outputs from all nodes in the layer.
        """
        layer_outputs: Dict[str, Any] = {}

        if self.max_workers is not None and len(layer) > 1:
            # Parallel execution
            layer_outputs = self._execute_layer_parallel(
                layer, workflow, context, state_tracker, failed_nodes,
                completed_nodes, run_id, start_node_index
            )
        else:
            # Sequential execution
            for i, node in enumerate(layer):
                node_index = start_node_index + i

                if node.name in completed_nodes:
                    state_tracker.mark_skipped(node.name)
                    if self._progress_tracker is not None:
                        self._progress_tracker.skip_node(node.name)
                    continue

                if self._has_failed_dependency(node, failed_nodes):
                    state_tracker.mark_skipped(node.name)
                    if self._progress_tracker is not None:
                        self._progress_tracker.skip_node(node.name)
                    continue

                outputs = self._execute_single_node(
                    node, workflow, context, state_tracker, failed_nodes,
                    run_id, node_index
                )
                if outputs:
                    layer_outputs.update(outputs)
                    context.update(outputs)

        return layer_outputs

    def _execute_layer_parallel(
        self,
        layer: List[Node],
        workflow: Workflow,
        context: Dict[str, Any],
        state_tracker: StateTracker,
        failed_nodes: set[str],
        completed_nodes: set[str],
        run_id: str,
        start_node_index: int,
    ) -> Dict[str, Any]:
        """Execute nodes in a layer using a thread pool."""
        layer_outputs: Dict[str, Any] = {}

        # Filter nodes that should be executed
        nodes_to_execute = [
            (i, node) for i, node in enumerate(layer)
            if node.name not in completed_nodes
            and not self._has_failed_dependency(node, failed_nodes)
        ]

        # Skip nodes that shouldn't run
        for i, node in enumerate(layer):
            if node.name in completed_nodes or self._has_failed_dependency(node, failed_nodes):
                state_tracker.mark_skipped(node.name)
                if self._progress_tracker is not None:
                    self._progress_tracker.skip_node(node.name)

        if not nodes_to_execute:
            return layer_outputs

        errors: List[Exception] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures: List[tuple[int, Node, Any]] = []
            for i, node in nodes_to_execute:
                future = executor.submit(
                    self._execute_single_node,
                    node, workflow, dict(context), state_tracker, failed_nodes,
                    run_id, start_node_index + i
                )
                futures.append((i, node, future))

            for _, node, future in futures:
                try:
                    outputs = future.result()
                    if outputs:
                        layer_outputs.update(outputs)
                except WorkflowExecutionError as exc:
                    errors.append(exc)
                    if self.fail_fast:
                        for _, _, pending in futures:
                            pending.cancel()
                        raise
                except Exception as exc:
                    errors.append(exc)
                    if self.fail_fast:
                        for _, _, pending in futures:
                            pending.cancel()
                        raise WorkflowExecutionError(
                            f"Node '{node.name}' failed: {exc}",
                            node_name=node.name,
                            original_error=exc,
                        ) from exc

        if errors and not self.fail_fast:
            logger.warning("Parallel layer completed with %d error(s)", len(errors))

        return layer_outputs

    def _execute_single_node(
        self,
        node: Node,
        workflow: Workflow,
        context: Dict[str, Any],
        state_tracker: StateTracker,
        failed_nodes: set[str],
        run_id: str,
        node_index: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a single node with full lifecycle handling.

        Returns the node outputs, or None if the node failed.
        """
        logger.debug(f"Executing node {node.name} at index {node_index}")

        # Gather inputs for this node
        node_inputs = self._gather_inputs(node, workflow, context)

        # Emit before_node hook
        self._emit(HookEvent.BEFORE_NODE, node, node_inputs)
        if self._progress_tracker is not None:
            self._progress_tracker.start_node(node.name)

        try:
            with LogContextManager(
                run_id=run_id,
                workflow_name=workflow.name,
                node_name=node.name,
            ):
                outputs = self._execute_node(node, workflow, context, state_tracker, node_inputs)

            # Emit after_node hook
            self._emit(HookEvent.AFTER_NODE, node, node_inputs, outputs)
            if self._progress_tracker is not None:
                self._progress_tracker.complete_node(node.name, outputs)

            if self._checkpoint_manager and node.is_checkpointable:
                self._checkpoint_manager.save(
                    workflow_name=workflow.name,
                    node_name=node.name,
                    node_index=node_index,
                    data=outputs,
                    run_id=run_id,
                    context={**context, **outputs},
                    workflow_hash=workflow.structure_hash(),
                )

            return outputs

        except Exception as e:
            # Emit on_error hook
            self._emit(HookEvent.ON_ERROR, node, e, context)
            if self._progress_tracker is not None:
                self._progress_tracker.fail_node(node.name, str(e))

            failed_nodes.add(node.name)
            state_tracker.mark_failed(node.name, str(e))

            if self.fail_fast:
                raise WorkflowExecutionError(
                    f"Node '{node.name}' failed: {e}",
                    workflow_name=workflow.name,
                    node_name=node.name,
                    original_error=e,
                ) from e

            return None

    def _has_failed_dependency(self, node: Node, failed_nodes: set[str]) -> bool:
        """Check if any of the node's dependencies have failed."""
        return bool(set(node.dependencies) & failed_nodes)
