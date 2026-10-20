"""Views (Qt dialogs) of the Kartea game register screens.

This package provides the view classes of the player configuration
list and edit screens.

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
PlayerKarteaConfigListView
    Lists the player configurations, with search and CRUD actions.
PlayerKarteaConfigEditView
    Dialog to create or edit a player configuration.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "PlayerKarteaConfigEditView",
    "PlayerKarteaConfigListView",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .playerkarteaconfigeditview import PlayerKarteaConfigEditView
from .playerkarteaconfiglistview import PlayerKarteaConfigListView
