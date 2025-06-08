"""
meandra.orchestration.orchestrator
==================================

"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from meandra.core.workflow import workflow
from meandra.scheduling.scheduler import Scheduler
from meandra.monitoring.state_tracker import StateTracker
from meandra.datastore.io_handlers import DataProvider

class Orchestrator(ABC):
    """Abstract base class for controlling the execution of workflows."""

    @abstractmethod
    def execute_workflow(self, workflow: workflow, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        pass

class SchedulingOrchestrator(Orchestrator):
    """
    Runs a workflow with a scheduler.

    Examples
    --------
    >>> workflow = SequentialWorkflow()
    >>> inputs = {"input1": 1, "input2": 2}
    >>> scheduler = DependencyScheduler()
    >>> state_tracker = StateTracker()
    >>> data_provider = DataProvider()
    >>> orchestrator = SchedulingOrchestrator(scheduler, state_tracker, data_provider)
    >>> outputs = orchestrator.execute_workflow(workflow, inputs)
    """
    def __init__(self, scheduler: Scheduler, state_tracker: StateTracker, data_provider: DataProvider):
        self.scheduler = scheduler
        self.state_tracker = state_tracker
        self.data_provider = data_provider

    def execute_workflow(self, workflow):
        execution_order = self.scheduler.resolve_dependencies(workflow)
        for node in execution_order:
            node_id = id(node)
            if self.state_tracker.get_state(node_id) != "completed":
                inputs = self.data_provider.load("input_path_placeholder")  # Placeholder for input path
                outputs = node.execute(inputs)
                self.data_provider.save("output_path_placeholder", outputs)  # Placeholder for output path
                self.state_tracker.update_state(node_id, "completed")
