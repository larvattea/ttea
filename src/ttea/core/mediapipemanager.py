"""MediaPipe pose landmarker setup for the camera pipeline.

Builds a MediaPipe Tasks ``PoseLandmarker`` from the calibration
settings and exposes per-frame pose detection.
"""

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from ttea.service import CalibrationService
from ttea.util import PathConfig


class MediaPipeManager:
    """Create and hold the MediaPipe pose landmarker.

    The model file and detector options come from
    ``CalibrationService``.

    Attributes
    ----------
    service : CalibrationService
        Source of the MediaPipe settings.
    detector : mediapipe.tasks.python.vision.PoseLandmarker
        The configured pose landmarker.

    Notes
    -----
    On a Raspberry Pi the embedded model is loaded
    (``get_mediapipe_model_embedded``); on other systems the desktop
    model (``get_mediapipe_model_desktop``). Both are resolved with
    ``PathConfig.model``.

    The running mode, number of poses and the minimum detection,
    presence and tracking confidences are also read from the
    service when the object is created.
    """

    def __init__(self):
        self.service = CalibrationService()

        if self.service.is_raspberry_pi():
            model_path = PathConfig.model(
                self.service.get_mediapipe_model_embedded()
            )
        else:
            model_path = PathConfig.model(
                self.service.get_mediapipe_model_desktop()
            )

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=self.service.get_mediapipe_execution_mode(),
            num_poses=self.service.get_mediapipe_num_position(),
            min_pose_detection_confidence=self.service.get_mediapipe_detection_position(),
            min_pose_presence_confidence=self.service.get_mediapipe_detection_presence(),
            min_tracking_confidence=self.service.get_mediapipe_detection_tracking(),
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect_for_video(self, mp_image, timestamp_ms):
        """Run pose detection on one video frame.

        Parameters
        ----------
        mp_image : mediapipe.Image
            Frame to analyze, in SRGB format.
        timestamp_ms : int
            Frame timestamp in milliseconds.

        Returns
        -------
        mediapipe.tasks.python.vision.PoseLandmarkerResult
            Detection result, with ``pose_landmarks`` holding one
            landmark list per detected pose.

        Notes
        -----
        Only valid when the landmarker runs in VIDEO mode. MediaPipe
        requires ``timestamp_ms`` to increase monotonically between
        calls; ``CameraVideoThread.run`` takes care of that.
        """
        return self.detector.detect_for_video(mp_image, timestamp_ms)
