"""Game controllers of the KarTEA game (pygame side).

This package provides the match controller (rules and frame flow) and
the session recorder (persistence of the session, its events and the
player's configuration). Developed by the Larva UDESC team.

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
GameController
    Match rules and frame flow.
SessionRecorder
    Records the session row, its events and the config phase/level.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "GameController",
    "SessionRecorder",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .gamecontroller import GameController
from .sessionrecorder import SessionRecorder
