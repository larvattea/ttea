"""Core camera and calibration package of the T-TEA platform.

Developed by the Larva UDESC team.

This package provides the camera capture thread, MediaPipe pose
detection and filtering, and the geometry used to calibrate the
projection.

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
CalibrationMath
    Geometry helpers for projection (keystone) calibration.
CameraVideoThread
    Camera thread with pose detection and telemetry overlay.
MediaPipeFilter
    Image enhancement and landmark smoothing.
MediaPipeManager
    MediaPipe pose landmarker setup and detection.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

# Define the __all__ variable
__all__ = [
    "CalibrationMath",
    "CameraVideoThread",
    "MediaPipeFilter",
    "MediaPipeManager",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

# Import the submodules
from .calibrationmath import CalibrationMath
from .cameravideothread import CameraVideoThread
from .mediapipefilter import MediaPipeFilter
from .mediapipemanager import MediaPipeManager
