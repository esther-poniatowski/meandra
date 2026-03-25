"""
meandra.orchestration.orchestrator
==================================

Workflow execution orchestration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4
import inspect
import logging

from meandra.checkpoint.manager import CheckpointManager, ResumePlan
from meandra.configuration.mod import ConfigProvider
from meandra.core.errors import DependencyResolutionError, NodeExecutionError
from meandra.core.node import Node
from meandra.core.workflow import Workflow
from meandra.logging.context import LogContextManager
from meandra.monitoring.progress import ProgressTracker
from meandra.monitoring.retry import RetryConfig, execute_with_retry
from meandra.monitoring.state_tracker import InMemoryStateTracker, StateTracker
from meandra.scheduling.scheduler import DAGScheduler, Scheduler


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
        raise NotImplementedError


@dataclass
class WorkflowState:
    """Explicit runtime state segmented into workflow inputs and produced artifacts."""

    inputs: Dict[str, Any]
    artifacts: Dict[str, Any] = field(default_factory=dict)
    node_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_resume(
        cls,
        inputs: Dict[str, Any],
        snapshot: Dict[str, Dict[str, Any]],
    ) -> "WorkflowState":
        resumed_inputs = dict(snapshot.get("inputs", {}))
        resumed_inputs.update(inputs)
        artifacts = dict(snapshot.get("artifacts", {}))
        for key in resumed_inputs:
            artifacts.pop(key, None)
        return cls(inputs=resumed_inputs, artifacts=artifacts)

    def available_context(self) -> Dict[str, Any]:
        context = dict(self.inputs)
        context.update(self.artifacts)
        return context

    def record_node_outputs(self, node: Node, outputs: Dict[str, Any]) -> None:
        self.node_outputs[node.name] = dict(outputs)
        self.artifacts.update(outputs)

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        return {
            "inputs": dict(self.inputs),
            "artifacts": dict(self.artifacts),
        }


class InputResolver:
    """Resolve node inputs from the explicit workflow state."""

    def resolve(self, node: Node, workflow: Workflow, state: WorkflowState) -> Dict[str, Any]:
        context = state.available_context()
        if node.contract.input_names:
            missing = [key for key in node.contract.input_names if key not in context]
            if missing:
                raise KeyError(f"Missing inputs for node '{node.name}': {missing}")
            return {key: context[key] for key in node.contract.input_names}

        if node.contract.accepts_context:
            return context

        if node.dependencies:
            inferred: Dict[str, Any] = {}
            for dep_name in node.dependencies:
                dep = workflow.get_node(dep_name)
                for output_name in dep.contract.output_names:
                    if output_name in context:
                        inferred[output_name] = context[output_name]
            if not inferred:
                raise KeyError(
                    f"Node '{node.name}' has no explicit inputs and no dependency outputs"
                )
            return inferred

        return {}


class LifecycleEvents:
    """Manage lifecycle hooks separately from execution policy."""

    def __init__(self) -> None:
        self._hooks: Dict[HookEvent, List[Callable[..., Any]]] = {
            event: [] for event in HookEvent
        }

    def add_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        self._validate_hook_signature(event, callback)
        self._hooks[event].append(callback)

    def remove_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        if callback in self._hooks[event]:
            self._hooks[event].remove(callback)

    def emit(self, event: HookEvent, *args: Any) -> None:
        for callback in self._hooks[event]:
            try:
                callback(*args)
            except Exception as exc:
                logger.warning("Hook callback failed for %s: %s", event.value, exc)

    def _validate_hook_signature(self, event: HookEvent, callback: Callable[..., Any]) -> None:
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


class ResumePolicy:
    """Build explicit resume plans from checkpoint state."""

    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager],
        enabled: bool,
    ) -> None:
        self._checkpoint_manager = checkpoint_manager
        self._enabled = enabled

    def load(self, workflow: Workflow) -> Optional[ResumePlan]:
        if self._checkpoint_manager is None or not self._enabled:
            return None
        checkpoint = self._checkpoint_manager.load_latest(workflow.name)
        if checkpoint is None:
            return None
        return self._checkpoint_manager.build_resume_plan(workflow, checkpoint)


class ExecutionEngine:
    """Runtime engine composed from smaller collaborators instead of one sink object."""

    def __init__(
        self,
        *,
        lifecycle: LifecycleEvents,
        input_resolver: InputResolver,
        checkpoint_manager: Optional[CheckpointManager],
        progress_tracker: Optional[ProgressTracker],
        retry_config: Optional[RetryConfig],
        fail_fast: bool,
        max_workers: Optional[int],
    ) -> None:
        self._lifecycle = lifecycle
        self._input_resolver = input_resolver
        self._checkpoint_manager = checkpoint_manager
        self._progress_tracker = progress_tracker
        self._retry_config = retry_config
        self._fail_fast = fail_fast
        self._max_workers = max_workers

    def run(
        self,
        workflow: Workflow,
        layers: List[List[Node]],
        inputs: Dict[str, Any],
        state_tracker: StateTracker,
        run_id: str,
        resume_plan: Optional[ResumePlan] = None,
    ) -> WorkflowState:
        state = (
            WorkflowState.from_resume(inputs, resume_plan.state)
            if resume_plan is not None
            else WorkflowState(inputs=dict(inputs))
        )
        completed_nodes = set(resume_plan.completed_nodes) if resume_plan is not None else set()
        failed_nodes: set[str] = set()
        node_index = 0

        if self._progress_tracker is not None:
            self._progress_tracker.total_nodes = len(workflow)

        for layer in layers:
            self._execute_layer(
                layer=layer,
                workflow=workflow,
                state=state,
                state_tracker=state_tracker,
                failed_nodes=failed_nodes,
                completed_nodes=completed_nodes,
                run_id=run_id,
                start_node_index=node_index,
            )
            node_index += len(layer)

        return state

    def _execute_layer(
        self,
        layer: List[Node],
        workflow: Workflow,
        state: WorkflowState,
        state_tracker: StateTracker,
        failed_nodes: set[str],
        completed_nodes: set[str],
        run_id: str,
        start_node_index: int,
    ) -> None:
        if self._max_workers is not None and len(layer) > 1:
            self._execute_layer_parallel(
                layer,
                workflow,
                state,
                state_tracker,
                failed_nodes,
                completed_nodes,
                run_id,
                start_node_index,
            )
            return

        for index, node in enumerate(layer):
            node_index = start_node_index + index
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
            try:
                outputs = self._execute_single_node(
                    node=node,
                    workflow=workflow,
                    state=state,
                    state_tracker=state_tracker,
                    run_id=run_id,
                )
            except WorkflowExecutionError:
                failed_nodes.add(node.name)
                if self._fail_fast:
                    raise
                continue
            completed_nodes.add(node.name)
            state.record_node_outputs(node, outputs)
            self._save_checkpoint(
                workflow=workflow,
                node=node,
                node_index=node_index,
                outputs=outputs,
                run_id=run_id,
                state=state,
                completed_nodes=completed_nodes,
            )

    def _execute_layer_parallel(
        self,
        layer: List[Node],
        workflow: Workflow,
        state: WorkflowState,
        state_tracker: StateTracker,
        failed_nodes: set[str],
        completed_nodes: set[str],
        run_id: str,
        start_node_index: int,
    ) -> None:
        nodes_to_execute = [
            (index, node)
            for index, node in enumerate(layer)
            if node.name not in completed_nodes and not self._has_failed_dependency(node, failed_nodes)
        ]
        for node in layer:
            if node.name in completed_nodes or self._has_failed_dependency(node, failed_nodes):
                state_tracker.mark_skipped(node.name)
                if self._progress_tracker is not None:
                    self._progress_tracker.skip_node(node.name)
        if not nodes_to_execute:
            return

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [
                (
                    index,
                    node,
                    executor.submit(
                        self._execute_single_node,
                        node,
                        workflow,
                        state,
                        state_tracker,
                        run_id,
                    ),
                )
                for index, node in nodes_to_execute
            ]
            for index, node, future in futures:
                try:
                    outputs = future.result()
                except WorkflowExecutionError:
                    failed_nodes.add(node.name)
                    if self._fail_fast:
                        for _, _, pending in futures:
                            pending.cancel()
                        raise
                    continue
                completed_nodes.add(node.name)
                state.record_node_outputs(node, outputs)
                self._save_checkpoint(
                    workflow=workflow,
                    node=node,
                    node_index=start_node_index + index,
                    outputs=outputs,
                    run_id=run_id,
                    state=state,
                    completed_nodes=completed_nodes,
                )

    def _execute_single_node(
        self,
        node: Node,
        workflow: Workflow,
        state: WorkflowState,
        state_tracker: StateTracker,
        run_id: str,
    ) -> Dict[str, Any]:
        logger.debug("Executing node %s", node.name)
        node_inputs = self._input_resolver.resolve(node, workflow, state)
        self._lifecycle.emit(HookEvent.BEFORE_NODE, node, node_inputs)
        if self._progress_tracker is not None:
            self._progress_tracker.start_node(node.name)
        try:
            with LogContextManager(
                run_id=run_id,
                workflow_name=workflow.name,
                node_name=node.name,
            ):
                outputs = self._execute_node(node, state_tracker, node_inputs)
            self._lifecycle.emit(HookEvent.AFTER_NODE, node, node_inputs, outputs)
            if self._progress_tracker is not None:
                self._progress_tracker.complete_node(node.name, outputs)
            return outputs
        except Exception as exc:
            self._lifecycle.emit(HookEvent.ON_ERROR, node, exc, state.available_context())
            if self._progress_tracker is not None:
                self._progress_tracker.fail_node(node.name, str(exc))
            state_tracker.mark_failed(node.name, str(exc))
            raise WorkflowExecutionError(
                f"Node '{node.name}' failed: {exc}",
                workflow_name=workflow.name,
                node_name=node.name,
                original_error=exc,
            ) from exc

    def _execute_node(
        self,
        node: Node,
        state_tracker: StateTracker,
        node_inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        state_tracker.mark_running(node.name)
        if self._retry_config is not None:
            outputs = execute_with_retry(node.execute, self._retry_config, None, node_inputs)
        else:
            outputs = node.execute(node_inputs)
        state_tracker.mark_completed(node.name, outputs)
        return outputs

    def _save_checkpoint(
        self,
        *,
        workflow: Workflow,
        node: Node,
        node_index: int,
        outputs: Dict[str, Any],
        run_id: str,
        state: WorkflowState,
        completed_nodes: set[str],
    ) -> None:
        if self._checkpoint_manager is None or not node.is_checkpointable:
            return
        self._checkpoint_manager.save(
            workflow_name=workflow.name,
            node_name=node.name,
            node_index=node_index,
            data=outputs,
            run_id=run_id,
            context=state.available_context(),
            workflow_hash=workflow.structure_hash(),
            workflow_state=state.snapshot(),
            completed_nodes=sorted(completed_nodes),
        )

    @staticmethod
    def _has_failed_dependency(node: Node, failed_nodes: set[str]) -> bool:
        return bool(set(node.dependencies) & failed_nodes)


class SchedulingOrchestrator(Orchestrator):
    """Execute workflows using explicit runtime services and a scheduler."""

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
        self.scheduler = scheduler or DAGScheduler()
        self._state_tracker = state_tracker
        self._progress_tracker = progress_tracker
        self._lifecycle = LifecycleEvents()
        self._resume_policy = ResumePolicy(checkpoint_manager, resume_from_checkpoint)
        self._engine = ExecutionEngine(
            lifecycle=self._lifecycle,
            input_resolver=InputResolver(),
            checkpoint_manager=checkpoint_manager,
            progress_tracker=progress_tracker,
            retry_config=retry_config,
            fail_fast=fail_fast,
            max_workers=max_workers,
        )

    def add_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        self._lifecycle.add_hook(event, callback)

    def remove_hook(self, event: HookEvent, callback: Callable[..., Any]) -> None:
        self._lifecycle.remove_hook(event, callback)

    def run(self, workflow: Workflow, inputs: Dict[str, Any] | ConfigProvider) -> Dict[str, Any]:
        run_id = str(uuid4())[:8]
        state_tracker = self._state_tracker or InMemoryStateTracker(workflow.name, run_id)
        logger.info("Starting workflow '%s' (run_id=%s)", workflow.name, run_id)

        if isinstance(inputs, ConfigProvider):
            inputs.resolve()
            inputs_dict = inputs.to_dict()
        else:
            inputs_dict = dict(inputs)

        with LogContextManager(run_id=run_id, workflow_name=workflow.name):
            self._lifecycle.emit(HookEvent.BEFORE_WORKFLOW, workflow, inputs_dict)
            try:
                layers = self.scheduler.resolve(workflow)
            except Exception as exc:
                raise DependencyResolutionError(str(exc), workflow_name=workflow.name) from exc
            resume_plan = self._resume_policy.load(workflow)
            state = self._engine.run(
                workflow=workflow,
                layers=layers,
                inputs=inputs_dict,
                state_tracker=state_tracker,
                run_id=run_id,
                resume_plan=resume_plan,
            )
            outputs = state.available_context()
            self._lifecycle.emit(HookEvent.AFTER_WORKFLOW, workflow, inputs_dict, outputs)
            if self._progress_tracker is not None:
                self._progress_tracker.finish()
            logger.info("Workflow '%s' completed (run_id=%s)", workflow.name, run_id)
            return outputs
