"""
meandra.scheduling.scheduler
============================

"""

from abc import ABC, abstractmethod

from meandra.core.workflow import workflow

class Scheduler(ABC):
    """Abstract base class for scheduling tasks within a workflow."""

    @abstractmethod
    def resolve_dependencies(self, workflow: workflow) -> None:
        """Determine execution order based on inter-task dependencies."""
        pass


# FIXME: Mock implementations for Scheduler
class MockScheduler(Scheduler):
    """Basic scheduler that orders nodes sequentially."""
    def resolve_dependencies(self, workflow):
        return workflow.nodes  # Assume nodes are already in execution order
