"""
udescjoinvilletteacontroller

A Python package for controller classes from the T-TEA platform,
supporting controller logic and data management from views.
Developed by the Larva UDESC team.

This package provides the controller classes for views, for the T-TEA platform.

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
LanguageController
    Manages language-related operations and data.
PlayerEditController
    Supports creation and editing of player profiles.
PlayerListController
    Manages the display and organization of player data.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

# Define the __all__ variable
__all__ = [
    "CalibrationController",
    "LanguageController",
    "MainController",
    "PlayerEditController",
    "PlayerListController",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

# Import the submodules
from .calibrationcontroller import CalibrationController
from .languagecontroller import LanguageController
from .maincontroller import MainController
from .playereditcontroller import PlayerEditController
from .playerlistcontroller import PlayerListController
