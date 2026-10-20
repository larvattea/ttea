"""Data models of the T-TEA platform.

Developed by the Larva UDESC team.

This package provides models for data representation and
manipulation.

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
AppModel
    Global application state (current language).
Calibration
    Camera, screen and projection area calibration.
CalibrationPoint
    Corner points of the calibrated projection.
CalibrationSetting
    MediaPipe, OpenCV, filter and window settings.
GameMetadata
    Game metadata read from ``metadata.json``.
InstitutionFacility
    Institution or facility where the platform is used.
Language
    Supported languages.
Player
    Player data.
Professional
    Professional linked to an institution or facility.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "AppModel",
    "Calibration",
    "CalibrationPoint",
    "CalibrationSetting",
    "GameMetadata",
    "Professional",
    "InstitutionFacility",
    "Language",
    "Player",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .appmodel import AppModel
from .calibration import Calibration
from .calibrationpoint import CalibrationPoint
from .calibrationsetting import CalibrationSetting
from .gamemetadata import GameMetadata
from .institutionfacility import InstitutionFacility
from .language import Language
from .player import Player
from .professional import Professional
