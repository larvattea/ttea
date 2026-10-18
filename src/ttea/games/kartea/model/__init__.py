"""Data models of the Kartea game.

This package provides the models for the player's game configuration,
the game phases and levels, and the recorded game sessions.

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
PlayerKarteaConfig
    Model for managing player configuration data.
PlayerKarteaSession
    Summary of a player's game session.
PlayerKarteaSessionDetail
    One event recorded during a game session.
KarteaPhase, KarteaPhaseLevel
    Game phases and their levels, read from the phase CSV files.
LevelRules
    Rules of a level used while the game is running.
CameraConfig, PoseTrackingConfig
    Hardware values handed to the camera and pose tracking.
ReflexiveModel, initialize_reflexive
    Common base of the data models (``set_data``/``get_data``).

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

__all__ = [
    "CameraConfig",
    "KarteaPhase",
    "KarteaPhaseLevel",
    "LevelRules",
    "PlayerKarteaConfig",
    "PlayerKarteaSession",
    "PlayerKarteaSessionDetail",
    "PoseTrackingConfig",
    "ReflexiveModel",
    "initialize_reflexive",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .hardwareconfig import CameraConfig, PoseTrackingConfig
from .karteaphase import KarteaPhase
from .karteaphaselevel import KarteaPhaseLevel
from .levelrules import LevelRules
from .playerkarteaconfig import PlayerKarteaConfig
from .playerkarteasession import PlayerKarteaSession
from .playerkarteasessiondetail import PlayerKarteaSessionDetail
from .reflexivemodel import ReflexiveModel, initialize_reflexive
