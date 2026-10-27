"""Service classes of the T-TEA platform.

Developed by the Larva UDESC team.

This package provides the service layer (business rules) used by the
controllers of the T-TEA platform.

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
CalibrationService
    Screens, cameras and calibration data.
CalibrationSettingService
    Calibration settings (MediaPipe, OpenCV, filters...).
HelpService
    Compiled help files, languages and topics.
HelpUnavailableError
    Raised when the help cannot be opened.
InstitutionFacilityService
    Business rules of institutions/facilities.
LanguageService
    Language detection, persistence and translators.
MainService
    Global actions of the main window.
PlayerGameLaunchService
    Data of the game launch screen.
PlayerService
    Business rules of players.
ProfessionalService
    Business rules of professionals.
TsdkService
    TSDK, the runtime of ``.ttea`` games, run through uv.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "CalibrationService",
    "CalibrationSettingService",
    "HelpService",
    "HelpUnavailableError",
    "ProfessionalService",
    "InstitutionFacilityService",
    "LanguageService",
    "MainService",
    "PlayerGameLaunchService",
    "PlayerService",
    "TsdkService",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .calibrationservice import CalibrationService
from .calibrationsettingservice import CalibrationSettingService
from .helpservice import HelpService, HelpUnavailableError
from .institutionfacilityservice import InstitutionFacilityService
from .languageservice import LanguageService
from .mainservice import MainService
from .playergamelaunchservice import PlayerGameLaunchService
from .playerservice import PlayerService
from .professionalservice import ProfessionalService
from .tsdkservice import TsdkService
