"""
meandra.configuration
=====================

Implements configuration management for structured, hierarchical, and dynamic parameter handling.

The `configurations` module provides mechanisms for parsing, merging, validating, and overriding
configuration parameters at runtime. The configuration system is designed for seamless integration
with the Meandra framework.

Modules
-------

"""

from meandra.configuration.mod import ConfigProvider

__all__ = ["ConfigProvider"]
