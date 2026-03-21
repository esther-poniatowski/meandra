"""
meandra.configuration
=====================

Configuration provider interface for Meandra.
"""

from typing import Protocol, Any, Dict, runtime_checkable


@runtime_checkable
class ConfigProvider(Protocol):
    """
    Minimal configuration provider interface.

    Implementations should adapt Hydra, Tessara, or custom config systems.
    """

    def get(self, path: str) -> Any:
        """Retrieve a value by dotted path."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Return a resolved dictionary representation."""
        ...

    def resolve(self) -> None:
        """Resolve interpolations or dynamic values."""
        ...

    def snapshot(self, path: str) -> None:
        """Persist a configuration snapshot."""
        ...
