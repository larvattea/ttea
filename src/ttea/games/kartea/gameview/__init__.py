"""Game views of the KarTEA game (pygame side).

This package provides what is drawn over the road during and between
matches: the HUD, the hit/miss feedback and the menus. Developed by
the Larva UDESC team.

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
HudView
    Score, time, phase and level shown during the game.
FeedbackView
    Hit/miss sound and image of a removed object.
Menu
    Start, pause and feedback menus.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "FeedbackView",
    "HudView",
    "Menu",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .feedbackview import FeedbackView
from .hudview import HudView
from .menu import Menu
