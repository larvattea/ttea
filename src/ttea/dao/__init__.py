"""Data Access Objects (DAOs) of the T-TEA platform.

Developed by the Larva UDESC team.

This package provides the DAO classes that persist the models in
CSV and INI files.

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
DAO
    Generic interface for CRUD operations.
CalibrationIniDAO
    Calibration data in an INI file.
CalibrationPointCsvDAO
    Calibration corner points in a CSV file.
CalibrationSettingIniDAO
    Calibration settings in an INI file.
InstitutionFacilityCsvDAO
    Institutions/facilities, one CSV file each.
PlayerCsvDAO
    Players, one CSV file each.
ProfessionalCsvDAO
    Professionals, one CSV file each.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "CalibrationIniDAO",
    "CalibrationPointCsvDAO",
    "CalibrationSettingIniDAO",
    "DAO",
    "ProfessionalCsvDAO",
    "InstitutionFacilityCsvDAO",
    "PlayerCsvDAO",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .calibrationinidao import CalibrationIniDAO
from .calibrationpointcsvdao import CalibrationPointCsvDAO
from .calibrationsettinginidao import CalibrationSettingIniDAO
from .dao import DAO
from .institutionfacilitycsvdao import InstitutionFacilityCsvDAO
from .playercsvdao import PlayerCsvDAO
from .professionalcsvdao import ProfessionalCsvDAO
