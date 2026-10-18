"""Controllers of the Kartea game register screens.

This package provides the controller classes (MVCS) that handle the
user interactions of the player configuration list and edit screens.

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
PlayerKarteaConfigListController
    Controller of the player configuration list screen.
PlayerKarteaConfigEditController
    Controller of the player configuration create/edit dialog.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

__all__ = [
    "PlayerKarteaConfigEditController",
    "PlayerKarteaConfigListController",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .playerkarteaconfigeditcontroller import PlayerKarteaConfigEditController
from .playerkarteaconfiglistcontroller import PlayerKarteaConfigListController
