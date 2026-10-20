"""Data access objects (DAOs) of the Kartea game.

This package provides the DAO classes for the player configuration,
the game phases and levels, and the game sessions and their events.

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
BaseCsvDAO
    Generic CRUD of a model stored in one CSV file per player.
ReadOnlyDAO
    Base of the read-only DAOs.
PlayerKarteaConfigCsvDAO
    Data Access Object for managing player kartea configuration data
    in CSV format.
PlayerKarteaSessionCsvDAO, PlayerKarteaSessionDetailCsvDAO
    Game sessions and their events, in CSV format.
KarteaPhaseCsvDAO, KarteaPhaseLevelCsvDAO
    Read-only access to the phase CSV files and their levels.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "BaseCsvDAO",
    "KarteaPhaseCsvDAO",
    "KarteaPhaseLevelCsvDAO",
    "PlayerKarteaConfigCsvDAO",
    "PlayerKarteaSessionCsvDAO",
    "PlayerKarteaSessionDetailCsvDAO",
    "ReadOnlyDAO",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .basecsvdao import BaseCsvDAO
from .karteaphasecsvdao import KarteaPhaseCsvDAO
from .karteaphaselevelcsvdao import KarteaPhaseLevelCsvDAO
from .playerkarteaconfigcsvdao import PlayerKarteaConfigCsvDAO
from .playerkarteasessioncsvdao import PlayerKarteaSessionCsvDAO
from .playerkarteasessiondetailcsvdao import PlayerKarteaSessionDetailCsvDAO
from .readonlydao import ReadOnlyDAO
