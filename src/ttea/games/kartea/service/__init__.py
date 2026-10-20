"""Service classes (MVCS) of the Kartea game.

This package provides the business rules used by the controllers and by
the game: player configuration, phases and levels, hardware values and
game sessions, for the T-TEA platform. Developed by the Larva UDESC
team.

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
PlayerKarteaConfigService
    Business rules of the player configuration.
KarteaPhaseService
    Phases, levels, progression and level rules.
KarteaHardwareService
    Screen, camera, calibration and MediaPipe values.
PlayerKarteaSessionService, PlayerKarteaSessionDetailService
    Game sessions and their events.
CsvCrudService
    Generic create/update/find service over a DAO.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "CsvCrudService",
    "KarteaHardwareService",
    "KarteaPhaseService",
    "PlayerKarteaConfigService",
    "PlayerKarteaSessionDetailService",
    "PlayerKarteaSessionService",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .csvcrudservice import CsvCrudService
from .karteahardwareservice import KarteaHardwareService
from .karteaphaseservice import KarteaPhaseService
from .playerkarteaconfigservice import PlayerKarteaConfigService
from .playerkarteasessiondetailservice import PlayerKarteaSessionDetailService
from .playerkarteasessionservice import PlayerKarteaSessionService
