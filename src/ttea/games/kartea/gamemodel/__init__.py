"""Game models of the KarTEA game (pygame side).

This package provides the objects drawn and moved during a match: the
pseudo-3D road, the car, targets and obstacles, plus image and sound
loading helpers. Developed by the Larva UDESC team.

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
Background
    Renders the horizon, the pseudo-3D road and its sprites.
Line
    One segment of the pseudo-3D road.
Car
    Car controlled by the player's feet.
Target, Obstacle, KillResult
    Objects on the road and the result of removing one.
Image, Sound
    Loading of images and sounds from files or Qt resources.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "Background",
    "Car",
    "Image",
    "KillResult",
    "Line",
    "Obstacle",
    "Sound",
    "Target",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .background import Background
from .car import Car
from .image import Image
from .line import Line
from .obstacle import Obstacle
from .sound import Sound
from .target import KillResult, Target
