"""Controller classes of the T-TEA platform.

Developed by the Larva UDESC team.

This package provides the controllers that connect the views to the
services of the T-TEA platform.

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
AutomaticCalibrationController
    Automatic calibration with a ChArUco board.
CalibrationController
    Hardware data and camera preview of the calibration.
CalibrationSettingController
    Calibration settings window.
HelpController
    Opens the help window on the topic of the active screen.
InstitutionFacilityEditController
    Edit/create dialog of institutions/facilities.
InstitutionFacilityListController
    List window of institutions/facilities.
LanguageController
    Language selection window.
MainController
    Main window: menus, dialogs and exit.
ManualCalibrationController
    Manual calibration by clicking the corners.
PlayerEditController
    Edit/create dialog of players.
PlayerGameLaunchController
    Game launch window and game process.
PlayerListController
    List window of players.
ProfessionalEditController
    Edit/create dialog of professionals.
ProfessionalListController
    List window of professionals.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "AutomaticCalibrationController",
    "CalibrationController",
    "CalibrationSettingController",
    "HelpController",
    "InstitutionFacilityEditController",
    "InstitutionFacilityListController",
    "LanguageController",
    "MainController",
    "ManualCalibrationController",
    "ProfessionalEditController",
    "ProfessionalListController",
    "PlayerEditController",
    "PlayerGameLaunchController",
    "PlayerListController",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .automaticcalibrationcontroller import AutomaticCalibrationController
from .calibrationcontroller import CalibrationController
from .calibrationsettingcontroller import CalibrationSettingController
from .helpcontroller import HelpController
from .institutionfacilityeditcontroller import \
    InstitutionFacilityEditController
from .institutionfacilitylistcontroller import \
    InstitutionFacilityListController
from .languagecontroller import LanguageController
from .maincontroller import MainController
from .manualcalibrationcontroller import ManualCalibrationController
from .playereditcontroller import PlayerEditController
from .playergamelaunchcontroller import PlayerGameLaunchController
from .playerlistcontroller import PlayerListController
from .professionaleditcontroller import ProfessionalEditController
from .professionallistcontroller import ProfessionalListController
