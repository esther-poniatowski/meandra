"""
Entry point for the `meandra` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m meandra


See Also
--------
meandra.cli: Module implementing the application's command-line interface.
"""
from .cli import app

app()
