"""
meandra.datastore.io_handlers
=============================

"""

from abc import ABC, abstractmethod
from typing import Any

class IOHandler(ABC):
    """Abstract base class for handling input/output data operations."""

    @abstractmethod
    def read(self, path):
        """Load data from a given path."""
        pass

    @abstractmethod
    def write(self, path, data):
        """Save data to a given path."""
        pass

    @abstractmethod
    def load(self, key: str) -> Any:
        """Load data by key."""
        pass

    @abstractmethod
    def save(self, key: str, data: Any) -> None:
        """Save data to a storage location determined by a key."""
        pass


# FIXME: Mock implementations for IOHandler
class MockIOHandler(IOHandler):
    def load(self, path):
        return "mock_data"  # Placeholder for actual data loading

    def save(self, path, data):
        print(f"Data saved to {path}: {data}")
