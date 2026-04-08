"""
meandra.datastore.catalog
=========================

Data catalog for named dataset management.

Classes
-------
DatasetEntry
    Entry in the data catalog.
DataCatalog
    Named dataset registry with path templating.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Set
import logging
import re
import string

from meandra.datastore.io_handlers import IOHandler, HandlerRegistry


logger = logging.getLogger(__name__)


@dataclass
class DatasetEntry:
    """
    Entry in the data catalog.

    Attributes
    ----------
    name : str
        Logical name for the dataset.
    path_template : str
        Path template with optional placeholders.
    handler : Optional[IOHandler]
        Handler for this dataset.
    description : str
        Description of the dataset.
    metadata : Dict[str, Any]
        Additional metadata for the entry.
    """

    name: str
    path_template: str
    handler: Optional[IOHandler] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def resolve_path(self, **kwargs: Any) -> Path:
        """
        Resolve path template with provided values.

        Supports placeholders: {run_id}, {date}, {timestamp}, and custom keys.

        Parameters
        ----------
        **kwargs : Any
            Values to substitute into the path template.

        Returns
        -------
        Path
            Resolved path.
        """
        # Add default placeholders
        defaults = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        }
        values = {**defaults, **kwargs}

        # Resolve template using format placeholders
        formatter = string.Formatter()
        fields = [field for _, field, _, _ in formatter.parse(self.path_template) if field]
        missing = [field for field in fields if field not in values]
        if missing:
            raise ValueError(f"Unresolved placeholders in path: {missing}")

        resolved = self.path_template.format(**values)

        # Check for unresolved placeholders
        unresolved = re.findall(r"\{(\w+)\}", resolved)
        if unresolved:
            raise ValueError(f"Unresolved placeholders in path: {unresolved}")

        return Path(resolved)

    def required_placeholders(self) -> Set[str]:
        """
        Return required placeholders in the path template.

        Placeholders with defaults (date, timestamp) are excluded.

        Returns
        -------
        Set[str]
            Set of required placeholder keys.
        """
        formatter = string.Formatter()
        fields = {field for _, field, _, _ in formatter.parse(self.path_template) if field}
        defaults = {"date", "timestamp"}
        return {field for field in fields if field not in defaults}


class DataCatalog:
    """
    Named dataset registry with path templating.

    The data catalog provides a central registry for datasets, mapping
    logical names to file paths and handlers. It supports path templating
    for dynamic path resolution.

    Parameters
    ----------
    base_dir : Optional[str | Path]
        Base directory for relative paths.
    registry : Optional[HandlerRegistry]
        Handler registry for format detection.

    Attributes
    ----------
    base_dir : Path
        Base directory for relative paths.

    Examples
    --------
    >>> catalog = DataCatalog("/data")
    >>>
    >>> # Register datasets
    >>> catalog.register("raw_data", "{run_id}/raw.npy")
    >>> catalog.register("processed", "{run_id}/processed.pkl", description="Processed output")
    >>>
    >>> # Save and load data
    >>> catalog.save("raw_data", data, run_id="run_001")
    >>> loaded = catalog.load("raw_data", run_id="run_001")

    With explicit handler:

    >>> from meandra.datastore import JSONHandler
    >>> catalog.register("config", "config.json", handler=JSONHandler())
    """

    def __init__(
        self,
        base_dir: Optional[str | Path] = None,
        registry: Optional[HandlerRegistry] = None,
    ):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._entries: Dict[str, DatasetEntry] = {}
        self._registry = registry or HandlerRegistry(register_defaults=True)

    def register(
        self,
        name: str,
        path_template: str,
        handler: Optional[IOHandler] = None,
        description: str = "",
        **metadata: Any,
    ) -> None:
        """
        Register a dataset in the catalog.

        Parameters
        ----------
        name : str
            Logical name for the dataset.
        path_template : str
            Path template with optional placeholders ({run_id}, {date}, etc.).
            Relative paths are resolved against base_dir.
        handler : Optional[IOHandler]
            Handler for this dataset. If None, inferred from extension.
        description : str
            Optional description of the dataset.
        **metadata : Any
            Additional metadata to store with the entry.

        Raises
        ------
        ValueError
            If a dataset with the same name is already registered.
        """
        if name in self._entries:
            raise ValueError(f"Dataset '{name}' is already registered")

        # Make path absolute if relative
        if not Path(path_template).is_absolute():
            path_template = str(self.base_dir / path_template)

        entry = DatasetEntry(
            name=name,
            path_template=path_template,
            handler=handler,
            description=description,
            metadata=metadata,
        )
        self._entries[name] = entry
        logger.debug(f"Registered dataset '{name}': {path_template}")

    def unregister(self, name: str) -> None:
        """
        Remove a dataset from the catalog.

        Parameters
        ----------
        name : str
            Name of the dataset to remove.
        """
        if name in self._entries:
            del self._entries[name]
            logger.debug(f"Unregistered dataset '{name}'")

    def get_entry(self, name: str) -> DatasetEntry:
        """
        Get a dataset entry by name.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        DatasetEntry
            The dataset entry.

        Raises
        ------
        KeyError
            If dataset is not registered.
        """
        if name not in self._entries:
            raise KeyError(f"Dataset '{name}' not found in catalog")
        return self._entries[name]

    def get_path(self, name: str, **kwargs: Any) -> Path:
        """
        Get the resolved path for a dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        **kwargs : Any
            Values for path template placeholders.

        Returns
        -------
        Path
            Resolved path.
        """
        entry = self.get_entry(name)
        return entry.resolve_path(**kwargs)

    def _get_handler(self, entry: DatasetEntry, path: Path) -> IOHandler:
        """
        Get handler for an entry, inferring from path if not specified.

        Parameters
        ----------
        entry : DatasetEntry
            The dataset entry.
        path : Path
            Resolved file path.

        Returns
        -------
        IOHandler
            Handler for the dataset.
        """
        if entry.handler is not None:
            return entry.handler
        return self._registry.get_handler(path)

    def save(self, name: str, data: Any, **kwargs: Any) -> Path:
        """
        Save data to a registered dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        data : Any
            Data to save.
        **kwargs : Any
            Values for path template placeholders.

        Returns
        -------
        Path
            Path where data was saved.
        """
        entry = self.get_entry(name)
        path = entry.resolve_path(**kwargs)
        handler = self._get_handler(entry, path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        handler.write(path, data)
        logger.info(f"Saved dataset '{name}' to {path}")
        return path

    def load(self, name: str, **kwargs: Any) -> Any:
        """
        Load data from a registered dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        **kwargs : Any
            Values for path template placeholders.

        Returns
        -------
        Any
            Loaded data.
        """
        entry = self.get_entry(name)
        path = entry.resolve_path(**kwargs)
        handler = self._get_handler(entry, path)

        data = handler.read(path)
        logger.info(f"Loaded dataset '{name}' from {path}")
        return data

    def exists(self, name: str, **kwargs: Any) -> bool:
        """
        Check if a dataset file exists.

        Parameters
        ----------
        name : str
            Name of the dataset.
        **kwargs : Any
            Values for path template placeholders.

        Returns
        -------
        bool
            True if the file exists.
        """
        try:
            path = self.get_path(name, **kwargs)
            return path.exists()
        except (KeyError, ValueError):
            return False

    def list_datasets(self) -> Dict[str, DatasetEntry]:
        """
        List all registered datasets.

        Returns
        -------
        Dict[str, DatasetEntry]
            Mapping of names to dataset entries.
        """
        return dict(self._entries)

    def required_placeholders(self, name: Optional[str] = None) -> Dict[str, Set[str]] | Set[str]:
        """
        Return required placeholders for one dataset or all datasets.

        Parameters
        ----------
        name : Optional[str]
            If provided, return placeholders for a single dataset.

        Returns
        -------
        Dict[str, Set[str]] | Set[str]
            Placeholder keys per dataset, or a single set for one dataset.
        """
        if name is not None:
            entry = self.get_entry(name)
            return entry.required_placeholders()
        return {entry.name: entry.required_placeholders() for entry in self._entries.values()}

    def __contains__(self, name: str) -> bool:
        """
        Check if a dataset is registered.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        bool
            True if the dataset is registered.
        """
        return name in self._entries

    def __len__(self) -> int:
        """
        Return number of registered datasets.

        Returns
        -------
        int
            Number of registered datasets.
        """
        return len(self._entries)
