"""
meandra.datastore.io_handlers
=============================

I/O handlers for various file formats.

Classes
-------
IOHandler
    Abstract base class for file I/O operations.
PickleHandler
    Handler for Python pickle files.
NumpyHandler
    Handler for NumPy array files.
JSONHandler
    Handler for JSON files.
YAMLHandler
    Handler for YAML files.
HandlerRegistry
    Registry of IOHandlers by file extension.

Functions
---------
register_handler
    Register a handler in the default registry.
register_default_handlers
    Register the default handlers if none are registered.
reset_default_registry
    Reset the default registry to a fresh state with default handlers.
get_handler
    Get appropriate handler for a file path.
read_file
    Read data from a file using the appropriate handler.
write_file
    Write data to a file using the appropriate handler.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union, List
import json
import pickle
import logging

logger = logging.getLogger(__name__)


class IOHandler(ABC):
    """
    Abstract base class for file I/O operations.

    Each handler supports specific file formats and provides read/write
    operations for data persistence.

    Attributes
    ----------
    EXTENSIONS : List[str]
        File extensions this handler supports.
    """

    EXTENSIONS: List[str] = []
    """File extensions this handler supports."""

    @classmethod
    def supports(cls, path: Union[str, Path]) -> bool:
        """
        Check if this handler supports the given file path.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        bool
            True if this handler supports the file extension.
        """
        suffix = Path(path).suffix.lower()
        return suffix in cls.EXTENSIONS

    @abstractmethod
    def read(self, path: Union[str, Path]) -> Any:
        """
        Read data from a file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Loaded data.
        """
        pass

    @abstractmethod
    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to a file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data to write.
        """
        pass


class PickleHandler(IOHandler):
    """
    Handler for Python pickle files.

    Supports arbitrary Python objects via pickle serialization.

    Examples
    --------
    >>> handler = PickleHandler()
    >>> handler.write("data.pkl", {"key": [1, 2, 3]})
    >>> data = handler.read("data.pkl")
    """

    EXTENSIONS = [".pkl", ".pickle"]

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read pickled data from file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Deserialized Python object.
        """
        path = Path(path)
        logger.debug(f"Reading pickle from {path}")
        with open(path, "rb") as f:
            return pickle.load(f)

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to pickle file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data to write.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Writing pickle to {path}")
        with open(path, "wb") as f:
            pickle.dump(data, f)


class NumpyHandler(IOHandler):
    """
    Handler for NumPy array files.

    Supports .npy (single array) and .npz (multiple arrays) formats.

    Examples
    --------
    >>> handler = NumpyHandler()
    >>> handler.write("array.npy", np.array([1, 2, 3]))
    >>> arr = handler.read("array.npy")
    """

    EXTENSIONS = [".npy", ".npz"]

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read NumPy array(s) from file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Loaded array or dict of arrays.
        """
        import numpy as np

        path = Path(path)
        logger.debug(f"Reading numpy from {path}")
        if path.suffix == ".npz":
            return dict(np.load(path))
        return np.load(path)

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write NumPy array(s) to file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data to write.
        """
        import numpy as np

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Writing numpy to {path}")
        if path.suffix == ".npz":
            if isinstance(data, dict):
                np.savez_compressed(path, **data)  # type: ignore[arg-type]
            else:
                np.savez_compressed(path, data=data)
        else:
            if not isinstance(data, np.ndarray):
                raise TypeError("NumpyHandler expects ndarray for .npy files")
            np.save(path, data)


class JSONHandler(IOHandler):
    """
    Handler for JSON files.

    Suitable for configuration and simple nested structures.

    Parameters
    ----------
    indent : int
        Number of spaces for JSON indentation.

    Attributes
    ----------
    indent : int
        Number of spaces for JSON indentation.

    Examples
    --------
    >>> handler = JSONHandler()
    >>> handler.write("config.json", {"key": "value"})
    >>> data = handler.read("config.json")
    """

    EXTENSIONS = [".json"]

    def __init__(self, indent: int = 2):
        self.indent = indent

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read JSON data from file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Deserialized JSON data.
        """
        path = Path(path)
        logger.debug(f"Reading JSON from {path}")
        with open(path, "r") as f:
            return json.load(f)

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to JSON file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data to write.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Writing JSON to {path}")
        with open(path, "w") as f:
            json.dump(data, f, indent=self.indent, default=str)


class YAMLHandler(IOHandler):
    """
    Handler for YAML files.

    Suitable for configuration and human-readable data.

    Examples
    --------
    >>> handler = YAMLHandler()
    >>> handler.write("config.yaml", {"key": "value"})
    >>> data = handler.read("config.yaml")
    """

    EXTENSIONS = [".yaml", ".yml"]

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read YAML data from file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Deserialized YAML data.
        """
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("pyyaml is required for YAML support") from exc
        path = Path(path)
        logger.debug(f"Reading YAML from {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to YAML file.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data to write.
        """
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("pyyaml is required for YAML support") from exc
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Writing YAML to {path}")
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


class HandlerRegistry:
    """
    Registry of IOHandlers by file extension.

    Provides isolation for handler registration, avoiding global state.
    Each registry instance maintains its own set of handlers.

    Parameters
    ----------
    register_defaults : bool
        If True, register default handlers on creation.

    Attributes
    ----------
    _handlers : Dict[str, IOHandler]
        Mapping of file extensions to their handlers.

    Examples
    --------
    >>> registry = HandlerRegistry()
    >>> registry.register(PickleHandler())
    >>> handler = registry.get_handler("data.pkl")
    """

    def __init__(self, register_defaults: bool = True):
        self._handlers: Dict[str, IOHandler] = {}
        if register_defaults:
            self.register_defaults()

    def register(self, handler: IOHandler) -> None:
        """
        Register a handler for its supported extensions.

        Parameters
        ----------
        handler : IOHandler
            Handler to register.
        """
        for ext in handler.EXTENSIONS:
            self._handlers[ext] = handler

    def register_defaults(self) -> None:
        """Register the default handlers (Pickle, Numpy, JSON, YAML)."""
        self.register(PickleHandler())
        self.register(NumpyHandler())
        self.register(JSONHandler())
        self.register(YAMLHandler())

    def get_handler(self, path: Union[str, Path]) -> IOHandler:
        """
        Get appropriate handler for a file path.

        Parameters
        ----------
        path : Union[str, Path]
            File path.

        Returns
        -------
        IOHandler
            Handler for the file format.

        Raises
        ------
        ValueError
            If no handler supports the file extension.
        """
        suffix = Path(path).suffix.lower()
        if suffix not in self._handlers:
            raise ValueError(f"No handler registered for extension '{suffix}'")
        return self._handlers[suffix]

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read data from a file using the appropriate handler.

        Parameters
        ----------
        path : Union[str, Path]
            File path.

        Returns
        -------
        Any
            Loaded data.
        """
        return self.get_handler(path).read(path)

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data to a file using the appropriate handler.

        Parameters
        ----------
        path : Union[str, Path]
            File path.
        data : Any
            Data to write.
        """
        self.get_handler(path).write(path, data)

    def clear(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()

    @property
    def extensions(self) -> List[str]:
        """
        List of registered extensions.

        Returns
        -------
        List[str]
            Registered file extensions.
        """
        return list(self._handlers.keys())

    def __contains__(self, ext: str) -> bool:
        """
        Check if an extension is registered.

        Parameters
        ----------
        ext : str
            File extension to check.

        Returns
        -------
        bool
            True if the extension has a registered handler.
        """
        return ext.lower() in self._handlers


# Lazily-initialised default registry (no mutable module-level dict).
_default_registry: HandlerRegistry | None = None


def _get_default_registry() -> HandlerRegistry:
    """
    Get or create the default registry.

    Returns
    -------
    HandlerRegistry
        The default handler registry.
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = HandlerRegistry(register_defaults=True)
    return _default_registry


def register_handler(handler: IOHandler) -> None:
    """
    Register a handler in the default registry.

    Parameters
    ----------
    handler : IOHandler
        Handler to register.
    """
    _get_default_registry().register(handler)


def register_default_handlers() -> None:
    """Register the default handlers if none are registered."""
    _get_default_registry()


def reset_default_registry() -> None:
    """
    Reset the default registry to a fresh state with default handlers.

    Useful for test isolation -- ensures no cross-test handler leakage.
    """
    global _default_registry
    _default_registry = HandlerRegistry(register_defaults=True)


def get_handler(path: Union[str, Path]) -> IOHandler:
    """
    Get appropriate handler for a file path.

    Parameters
    ----------
    path : Union[str, Path]
        File path.

    Returns
    -------
    IOHandler
        Handler for the file format.

    Raises
    ------
    ValueError
        If no handler supports the file extension.
    """
    return _get_default_registry().get_handler(path)


def read_file(path: Union[str, Path]) -> Any:
    """
    Read data from a file using the appropriate handler.

    Parameters
    ----------
    path : Union[str, Path]
        File path.

    Returns
    -------
    Any
        Loaded data.
    """
    return _get_default_registry().read(path)


def write_file(path: Union[str, Path], data: Any) -> None:
    """
    Write data to a file using the appropriate handler.

    Parameters
    ----------
    path : Union[str, Path]
        File path.
    data : Any
        Data to write.
    """
    _get_default_registry().write(path, data)
