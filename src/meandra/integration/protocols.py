"""
meandra.integration.protocols
=============================

Stable extension seams for workflow and IO integrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from meandra.core.node import Node
    from meandra.core.workflow import Workflow
    from morpha.io.savers import Saver
    from morpha.io.loaders import Loader


class NodeTransformer(Protocol):
    """Transform a node without depending on its concrete field layout."""

    def transform_node(self, node: "Node") -> "Node":
        ...


class WorkflowTransformer(Protocol):
    """Transform a workflow through the stable workflow seam."""

    def transform_workflow(self, workflow: "Workflow") -> "Workflow":
        ...


@dataclass(frozen=True)
class IOBackendDescriptor:
    """Descriptor for a data backend keyed by file extension."""

    extension: str
    saver_name: str
    loader_name: str

    def resolve_saver(self, module: Any) -> Optional[Type["Saver"]]:
        return getattr(module, self.saver_name, None)

    def resolve_loader(self, module: Any) -> Optional[Type["Loader"]]:
        return getattr(module, self.loader_name, None)
