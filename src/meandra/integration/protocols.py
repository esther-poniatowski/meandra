"""
meandra.integration.protocols
=============================

Stable extension seams for workflow and IO integrations.

Classes
-------
NodeTransformer
    Transform a node without depending on its concrete field layout.
WorkflowTransformer
    Transform a workflow through the stable workflow seam.
IOBackendDescriptor
    Descriptor for a data backend keyed by file extension.
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
        """
        Transform a single node.

        Parameters
        ----------
        node : Node
            The node to transform.

        Returns
        -------
        Node
            The transformed node.
        """
        ...


class WorkflowTransformer(Protocol):
    """Transform a workflow through the stable workflow seam."""

    def transform_workflow(self, workflow: "Workflow") -> "Workflow":
        """
        Transform a workflow.

        Parameters
        ----------
        workflow : Workflow
            The workflow to transform.

        Returns
        -------
        Workflow
            The transformed workflow.
        """
        ...


@dataclass(frozen=True)
class IOBackendDescriptor:
    """
    Descriptor for a data backend keyed by file extension.

    Attributes
    ----------
    extension : str
        File extension this backend handles.
    saver_name : str
        Name of the saver class in the backend module.
    loader_name : str
        Name of the loader class in the backend module.
    """

    extension: str
    saver_name: str
    loader_name: str

    def resolve_saver(self, module: Any) -> Optional[Type["Saver"]]:
        """
        Resolve the saver class from the given module.

        Parameters
        ----------
        module : Any
            Module to look up the saver class in.

        Returns
        -------
        Optional[Type[Saver]]
            The saver class, or None if not found.
        """
        return getattr(module, self.saver_name, None)

    def resolve_loader(self, module: Any) -> Optional[Type["Loader"]]:
        """
        Resolve the loader class from the given module.

        Parameters
        ----------
        module : Any
            Module to look up the loader class in.

        Returns
        -------
        Optional[Type[Loader]]
            The loader class, or None if not found.
        """
        return getattr(module, self.loader_name, None)
