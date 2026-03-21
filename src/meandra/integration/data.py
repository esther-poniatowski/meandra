"""
meandra.integration.data
========================

Integration adapters for Morpha data structures.

Classes
-------
DataStructureIOHandler
    IOHandler that bridges Meandra's I/O system with Morpha's Saver/Loader.
TypedNode
    Node with input/output type contracts for DataStructures.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, Callable
import logging

if TYPE_CHECKING:
    from morpha.io.savers import Saver
    from morpha.io.loaders import Loader
    from morpha.structures.base import DataStructure
    from meandra.core.node import Node

from meandra.datastore.io_handlers import IOHandler
from meandra.utils.typing import check_type

logger = logging.getLogger(__name__)


class DataStructureIOHandler(IOHandler):
    """
    IOHandler that bridges Meandra's I/O system with Morpha's Saver/Loader.

    Provides seamless integration between Meandra workflows and Morpha's
    type-safe data persistence layer.

    Attributes
    ----------
    saver_cls : Type[Saver]
        The Morpha Saver class to use for writing.
    loader_cls : Type[Loader]
        The Morpha Loader class to use for reading.

    Examples
    --------
    >>> from morpha.io.savers import SaverPKL
    >>> from morpha.io.loaders import LoaderPKL
    >>> handler = DataStructureIOHandler(SaverPKL, LoaderPKL)
    >>> handler.write("output.pkl", my_data_structure)
    >>> data = handler.read("output.pkl")
    """

    EXTENSIONS: List[str] = [".pkl", ".pickle", ".npy", ".npz", ".yaml", ".yml", ".json", ".h5", ".hdf5"]

    _EXTENSION_MAP: Dict[str, tuple[str, str]] = {
        ".pkl": ("SaverPKL", "LoaderPKL"),
        ".pickle": ("SaverPKL", "LoaderPKL"),
        ".npy": ("SaverNPY", "LoaderNPY"),
        ".npz": ("SaverNPZ", "LoaderNPZ"),
        ".yaml": ("SaverYAML", "LoaderYAML"),
        ".yml": ("SaverYAML", "LoaderYAML"),
        ".json": ("SaverJSON", "LoaderJSON"),
        ".h5": ("SaverHDF5", "LoaderHDF5"),
        ".hdf5": ("SaverHDF5", "LoaderHDF5"),
    }

    def __init__(
        self,
        saver_cls: Optional[Type["Saver"]] = None,
        loader_cls: Optional[Type["Loader"]] = None,
    ) -> None:
        """
        Initialize with Morpha Saver and Loader classes.

        Parameters
        ----------
        saver_cls : Type[Saver], optional
            Morpha Saver class for writing. If None, uses auto-detection.
        loader_cls : Type[Loader], optional
            Morpha Loader class for reading. If None, uses auto-detection.
        """
        self.saver_cls = saver_cls
        self.loader_cls = loader_cls

    def read(self, path: Union[str, Path]) -> Any:
        """
        Read data using Morpha's Loader.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.

        Returns
        -------
        Any
            Loaded data structure.
        """
        path = Path(path)

        if self.loader_cls is not None:
            loader = self.loader_cls(path)
            return loader.load()

        # Auto-detect loader based on extension
        loader_cls = self._get_loader_for_path(path)
        if loader_cls is None:
            raise ValueError(f"No loader found for extension: {path.suffix}")

        loader = loader_cls(path)
        return loader.load()

    def write(self, path: Union[str, Path], data: Any) -> None:
        """
        Write data using Morpha's Saver.

        Parameters
        ----------
        path : Union[str, Path]
            Path to the file.
        data : Any
            Data structure to write.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if self.saver_cls is not None:
            saver = self.saver_cls(path)
            saver.save(data)
            return

        # Auto-detect saver based on extension
        saver_cls = self._get_saver_for_path(path)
        if saver_cls is None:
            raise ValueError(f"No saver found for extension: {path.suffix}")

        saver = saver_cls(path)
        saver.save(data)

    def _get_loader_for_path(self, path: Path) -> Optional[Type["Loader"]]:
        """Get appropriate Loader class for file extension."""
        try:
            from morpha.io import loaders as morpha_loaders
            ext = path.suffix.lower()
            if ext not in self._EXTENSION_MAP:
                return None
            _, loader_name = self._EXTENSION_MAP[ext]
            loader_cls = getattr(morpha_loaders, loader_name, None)
            if loader_cls is None:
                raise ValueError(
                    f"Loader class '{loader_name}' not found for extension '{ext}'"
                )
            return loader_cls
        except ImportError:
            logger.warning("Morpha loaders not available")
            return None

    def _get_saver_for_path(self, path: Path) -> Optional[Type["Saver"]]:
        """Get appropriate Saver class for file extension."""
        try:
            from morpha.io import savers as morpha_savers
            ext = path.suffix.lower()
            if ext not in self._EXTENSION_MAP:
                return None
            saver_name, _ = self._EXTENSION_MAP[ext]
            saver_cls = getattr(morpha_savers, saver_name, None)
            if saver_cls is None:
                raise ValueError(
                    f"Saver class '{saver_name}' not found for extension '{ext}'"
                )
            return saver_cls
        except ImportError:
            logger.warning("Morpha savers not available")
            return None

    @classmethod
    def register_extension(cls, extension: str, saver_name: str, loader_name: str) -> None:
        """Register a custom Saver/Loader by extension."""
        if not extension.startswith("."):
            extension = f".{extension}"
        cls._EXTENSION_MAP[extension.lower()] = (saver_name, loader_name)
        if extension.lower() not in cls.EXTENSIONS:
            cls.EXTENSIONS.append(extension.lower())

    @classmethod
    def supports(cls, path: Union[str, Path]) -> bool:
        """Check if this handler supports the given file path."""
        suffix = Path(path).suffix.lower()
        return suffix in cls.EXTENSIONS


def create_typed_node(
    name: str,
    func: Callable[[Dict[str, Any]], Any],
    input_types: Optional[Dict[str, Type]] = None,
    output_types: Optional[Dict[str, Type]] = None,
    allow_missing_inputs: bool = False,
    allow_missing_outputs: bool = False,
    **kwargs: Any,
) -> "Node":
    """
    Create a Node with type validation contracts.

    Creates input and output contracts that validate data types,
    supporting both primitive types and Morpha DataStructure types.

    Parameters
    ----------
    name : str
        Node name.
    func : Callable
        Node function.
    input_types : Dict[str, Type], optional
        Mapping of input names to expected types.
    output_types : Dict[str, Type], optional
        Mapping of output names to expected types.
    **kwargs
        Additional arguments passed to Node constructor.

    Returns
    -------
    Node
        Node with type validation contracts.

    Examples
    --------
    >>> import numpy as np
    >>> def process(inputs):
    ...     return {"result": inputs["data"] * 2}
    >>>
    >>> node = create_typed_node(
    ...     "processor",
    ...     process,
    ...     input_types={"data": np.ndarray},
    ...     output_types={"result": np.ndarray},
    ... )
    """
    from meandra.core.node import Node

    def input_contract(inputs: Dict[str, Any]) -> None:
        if input_types is None:
            return
        for key, expected_type in input_types.items():
            if key not in inputs:
                if allow_missing_inputs:
                    continue
                raise KeyError(f"Missing required input '{key}'")
            value = inputs[key]
            if not check_type(value, expected_type):
                raise TypeError(
                    f"Input '{key}' expected {expected_type}, got {type(value)}"
                )

    def output_contract(outputs: Dict[str, Any]) -> None:
        if output_types is None:
            return
        for key, expected_type in output_types.items():
            if key not in outputs:
                if allow_missing_outputs:
                    continue
                raise KeyError(f"Missing required output '{key}'")
            value = outputs[key]
            if not check_type(value, expected_type):
                raise TypeError(
                    f"Output '{key}' expected {expected_type}, got {type(value)}"
                )

    return Node(
        name=name,
        func=func,
        input_contract=input_contract if input_types else None,
        output_contract=output_contract if output_types else None,
        **kwargs,
    )
