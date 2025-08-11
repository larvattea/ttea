"""
udescjoinvilletteawindow

A Python package for window management in the T-TEA platform,
supporting and configuration management. Developed by the
Larva UDESC team.

This package provides tools for handling window layouts,
and appearance settings.

Attributes
----------
__version__ : str
    The current version of the package.
__date__ : str
    The release date of this version.
__author__ : str
    The development team.
__license__ : str
    The license under which the package is distributed.

See Also
--------
ViewFactory
    Creates view instances for the application.
WindowConfig
    Manages window layout and appearance settings.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

# Define the __all__ variable
__all__ = [
    "WindowConfig",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

# Import the submodules
from .windowconfig import WindowConfig
