"""Hardware service of KarTEA (screen, camera, MediaPipe)."""

from ttea.games.kartea.model import CameraConfig, PoseTrackingConfig
from ttea.games.kartea.util import KarteaPathConfig
from ttea.model import CalibrationPoint
from ttea.service import CalibrationService


class KarteaHardwareService:
    """Hardware service (MVCS) of KarTEA.

    Covers screen, camera, calibration and MediaPipe. Kept apart from
    PlayerKarteaConfigService, which handles only the player
    configuration. It hands ready values to the game components
    (CameraConfig, PoseTrackingConfig, calibration points), so that
    Camera and PoseTracking do not depend on services.

    Parameters
    ----------
    calibration_service : CalibrationService | None, optional
        T-TEA service with the calibration and hardware data. Created if
        None. Kept private.
    """

    def __init__(self, calibration_service: CalibrationService | None = None):
        self._calibration = calibration_service or CalibrationService()

    # ======================
    # Screen
    # ======================
    def is_raspberry_pi(self) -> bool:
        """Check whether the game runs on a Raspberry Pi.

        Returns
        -------
        bool
            Value reported by the CalibrationService.
        """
        return self._calibration.is_raspberry_pi()

    def is_fullscreen(self) -> bool:
        """Check whether the game window is fullscreen.

        Returns
        -------
        bool
            Value reported by the CalibrationService.
        """
        return self._calibration.is_fullscreen()

    def get_screen_size(self) -> dict[str, int]:
        """Return the configured screen size.

        Returns
        -------
        dict[str, int]
            Dictionary from CalibrationService with ``width`` and
            ``height``.
        """
        return self._calibration.get_screen_size()

    def get_screen_info(self) -> dict[str, int]:
        """Return the configured screen position.

        Returns
        -------
        dict[str, int]
            Dictionary from CalibrationService with ``screen_position``,
            ``screen_pos_x`` and ``screen_pos_y``.
        """
        return self._calibration.get_screen_info()

    def get_screen_settings(self) -> dict[str, object]:
        """Return the screen settings in the GameSettings format.

        Returns
        -------
        dict[str, object]
            ``screen_width``, ``screen_height``, ``screen_os_index``,
            ``screen_pos_x``, ``screen_pos_y`` and ``fullscreen``.
        """
        size = self.get_screen_size()
        info = self.get_screen_info()
        return {
            "screen_width": size["width"],
            "screen_height": size["height"],
            "screen_os_index": info["screen_position"],
            "screen_pos_x": info["screen_pos_x"],
            "screen_pos_y": info["screen_pos_y"],
            "fullscreen": self.is_fullscreen(),
        }

    # ======================
    # Calibration
    # ======================
    def get_calibration_points(self) -> list[tuple[int, int]] | None:
        """Return the 4 points of the calibrated area.

        Returns
        -------
        list[tuple[int, int]] | None
            The (x, y) points 1 to 4 of the saved calibration, or None
            if there is no calibration.
        """
        point = self._calibration.find_by_id_calibration_point(
            CalibrationPoint.ID_VALUE
        )
        if point is None:
            return None
        return [
            (point.pointx1, point.pointy1),
            (point.pointx2, point.pointy2),
            (point.pointx3, point.pointy3),
            (point.pointx4, point.pointy4),
        ]

    # ======================
    # Camera, through OpenCV
    # ======================
    def get_camera_config(self) -> CameraConfig:
        """Return the camera configuration (OpenCV).

        Returns
        -------
        CameraConfig
            Camera index and OpenCV capture backend for the platform.
        """
        info = self._calibration.get_camera_info()
        return CameraConfig(
            camera_index=info["camera_position"],
            capture_backend=self._calibration.get_opencv_capture_backend(),
        )

    # ======================
    # MediaPipe
    # ======================
    def get_pose_tracking_config(self) -> PoseTrackingConfig:
        """Return the Pose Landmarker configuration for the platform.

        Returns
        -------
        PoseTrackingConfig
            Model path, running mode, number of poses and confidence
            thresholds from the CalibrationService.

        Notes
        -----
        On a Raspberry Pi the embedded MediaPipe model is used;
        elsewhere, the desktop model.
        """
        if self.is_raspberry_pi():
            model_name = self._calibration.get_mediapipe_model_embedded()
        else:
            model_name = self._calibration.get_mediapipe_model_desktop()

        return PoseTrackingConfig(
            model_path=KarteaPathConfig.model(model_name),
            running_mode=self._calibration.get_mediapipe_execution_mode(),
            num_poses=self._calibration.get_mediapipe_num_position(),
            min_pose_detection_confidence=(
                self._calibration.get_mediapipe_detection_position()
            ),
            min_pose_presence_confidence=(
                self._calibration.get_mediapipe_detection_presence()
            ),
            min_tracking_confidence=(
                self._calibration.get_mediapipe_detection_tracking()
            ),
        )
