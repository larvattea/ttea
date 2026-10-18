"""Hardware values handed to the game components.

``Camera`` and ``PoseTracking`` receive only these values, not a
service.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CameraConfig:
    """Camera configuration (OpenCV).

    Attributes
    ----------
    camera_index : int
        Index of the camera in the operating system.
    capture_backend : int
        OpenCV capture backend for the platform.
    """

    camera_index: int
    capture_backend: int


@dataclass(frozen=True)
class PoseTrackingConfig:
    """MediaPipe Pose Landmarker configuration.

    Attributes
    ----------
    model_path : str
        Path of the model (.task) already resolved for the platform.
    running_mode : Any
        MediaPipe running mode (e.g. VIDEO).
    num_poses : int
        Maximum number of detected poses.
    min_pose_detection_confidence : float
        Minimum confidence for a pose to be detected.
    min_pose_presence_confidence : float
        Minimum confidence for a pose to be considered present.
    min_tracking_confidence : float
        Minimum confidence for a pose to be considered tracked.
    """

    model_path: str
    running_mode: Any
    num_poses: int
    min_pose_detection_confidence: float
    min_pose_presence_confidence: float
    min_tracking_confidence: float
