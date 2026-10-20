"""Utilities of the Kartea game.

This package provides the central path management and the single
tables (resource fields, arrival times, kartea.ini defaults and track
palettes) shared by the configuration screens and the game. Developed
by the Larva UDESC team.

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
KarteaPathConfig
    Manages the KarTEA file paths, directories and Qt resources.
KarteaResourceFields, ResourceField
    Resource fields (image/sound) of the player configuration.
KarteaArrivalTimeFields, ArrivalTimeField
    Object arrival times by track speed.
KarteaIniDefaults
    Default values of kartea.ini.
KarteaPalettes, Palette
    Color palettes of the track.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "ArrivalTimeField",
    "KarteaArrivalTimeFields",
    "KarteaIniDefaults",
    "KarteaPalettes",
    "KarteaPathConfig",
    "KarteaResourceFields",
    "Palette",
    "ResourceField",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .arrivaltimefields import ArrivalTimeField, KarteaArrivalTimeFields
from .inidefaults import KarteaIniDefaults
from .karteapathconfig import KarteaPathConfig
from .palettes import KarteaPalettes, Palette
from .resourcefields import KarteaResourceFields, ResourceField
