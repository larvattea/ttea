"""Core input of the KarTEA game: camera, pose tracking and lanes.

This package captures the camera image, tracks the player's feet with
MediaPipe and turns the feet position into a lane. Developed by the
Larva UDESC team.

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
Camera
    Video capture (OpenCV) with the calibration area drawn.
PoseTracking
    Feet detection (MediaPipe) mapped to screen coordinates.
LaneDetector, OUT_OF_AREA
    Lane of the player from the feet x position.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

__all__ = [
    "OUT_OF_AREA",
    "Camera",
    "LaneDetector",
    "PoseTracking",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .camera import Camera
from .lanedetector import OUT_OF_AREA, LaneDetector
from .posetracking import PoseTracking
