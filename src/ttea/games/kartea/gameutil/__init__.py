"""Utilities of the KarTEA game (pygame side).

This package provides the immutable game settings, the mutable state
of a match and window helpers. Developed by the Larva UDESC team.

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
GameSettings
    Immutable game configuration: screen, sizes, colors and resources.
GameState, LevelStats, SessionStats
    Mutable state of a match and its level/session counters.
regain_focus
    Brings the pygame window back to the foreground.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

__all__ = [
    "GameSettings",
    "GameState",
    "LevelStats",
    "SessionStats",
    "regain_focus",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .gamesettings import GameSettings
from .gamestate import GameState, LevelStats, SessionStats
from .window import regain_focus
