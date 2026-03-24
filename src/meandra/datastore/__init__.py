"""
meandra.datastore
=================

Data I/O and catalog management.

This module provides:
- IOHandlers for reading/writing various file formats
- DataCatalog for named dataset management with path templating
"""

from meandra.datastore.io_handlers import (
    IOHandler,
    PickleHandler,
    NumpyHandler,
    JSONHandler,
    YAMLHandler,
    HandlerRegistry,
    register_handler,
    register_default_handlers,
    reset_default_registry,
    get_handler,
    read_file,
    write_file,
)
from meandra.datastore.catalog import (
    DataCatalog,
    DatasetEntry,
)

__all__ = [
    # IO Handlers
    "IOHandler",
    "PickleHandler",
    "NumpyHandler",
    "JSONHandler",
    "YAMLHandler",
    "HandlerRegistry",
    "register_handler",
    "register_default_handlers",
    "reset_default_registry",
    "get_handler",
    "read_file",
    "write_file",
    # Catalog
    "DataCatalog",
    "DatasetEntry",
]
