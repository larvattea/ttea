"""Calibration service: screens, cameras and calibration data.

Lists the screens and cameras, stores the hardware calibration and the
calibration points, and gives the camera pipeline access to the
calibration settings through ``CalibrationSettingService``.
"""

import os
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtMultimedia import QCameraDevice, QMediaDevices

from ttea.dao import CalibrationIniDAO, CalibrationPointCsvDAO
from ttea.model import Calibration, CalibrationPoint, CalibrationSetting

if TYPE_CHECKING:
    from ttea.service import CalibrationSettingService


class CalibrationService:
    """Business logic of the projection and camera calibration.

    Parameters
    ----------
    dao : CalibrationIniDAO | None, optional
        DAO of the hardware calibration. Default is None, which creates
        a new ``CalibrationIniDAO``.
    dao_calibration_point : CalibrationPointCsvDAO | None, optional
        DAO of the calibration points. Default is None, which creates a
        new ``CalibrationPointCsvDAO``.
    calibration_setting_service : CalibrationSettingService, optional
        Settings service to reuse. Default is None, which creates one on
        first use.

    Attributes
    ----------
    dao : CalibrationIniDAO
        DAO of the hardware calibration.
    dao_calibration_point : CalibrationPointCsvDAO
        DAO of the calibration points.

    Notes
    -----
    The ``get_mediapipe_*``, ``get_opencv_*``, ``get_filter_*``,
    ``is_*`` and calibration-mode getters only delegate to
    ``CalibrationSettingService``.
    """

    def __init__(
        self,
        dao: Optional[CalibrationIniDAO] = None,
        dao_calibration_point: Optional[CalibrationPointCsvDAO] = None,
        calibration_setting_service: Optional[
            "CalibrationSettingService"
        ] = None,
    ):
        # Optional cache, if the screens do not change while running:
        # self._screens = QGuiApplication.screens()
        self.dao = dao or CalibrationIniDAO()
        self.dao_calibration_point = (
            dao_calibration_point or CalibrationPointCsvDAO()
        )

        self._calibration_setting_service = calibration_setting_service

    @property
    def calibration_setting_service(self):
        """Settings service, created on first access if not injected."""
        if self._calibration_setting_service is None:
            from ttea.service import CalibrationSettingService

            self._calibration_setting_service = CalibrationSettingService(
                calibration_service=self
            )
        return self._calibration_setting_service

    def get_proportions(self) -> Dict[str, tuple[int, int]]:
        """Return the supported aspect ratios.

        Returns
        -------
        dict_items
            ``Calibration.PROPORTIONS.items()``: pairs of name (e.g.
            ``"16:9"``) and ``(width, height)``, despite the ``dict``
            annotation.
        """
        return Calibration.PROPORTIONS.items()

    def get_screens(self) -> List[QScreen]:
        """Return the screens currently connected.

        Returns
        -------
        list[QScreen]
            ``QGuiApplication.screens()``, read on every call.
        """
        return QGuiApplication.screens()

    def get_video_inputs(self) -> List[QCameraDevice]:
        """Return the cameras currently available.

        Returns
        -------
        list[QCameraDevice]
            ``QMediaDevices.videoInputs()``.
        """
        return QMediaDevices.videoInputs()

    def _get_screen(self, index: int) -> Optional[QScreen]:
        """Return the screen at ``index``, or None if out of range."""
        screens = self.get_screens()
        if 0 <= index < len(screens):
            return screens[index]
        return None

    def get_geometry_of_screen(self, index: int) -> Optional[QRect]:
        """Return the full geometry of a screen.

        Parameters
        ----------
        index : int
            Screen index in ``get_screens()``.

        Returns
        -------
        QRect | None
            ``QScreen.geometry()``, or None if the index is out of
            range.
        """
        screen = self._get_screen(index)
        return screen.geometry() if screen else None

    def get_available_geometry_of_screen(self, index: int) -> Optional[QRect]:
        """Return the available geometry of a screen.

        Parameters
        ----------
        index : int
            Screen index in ``get_screens()``.

        Returns
        -------
        QRect | None
            ``QScreen.availableGeometry()`` (without task bars and
            docks), or None if the index is out of range.
        """
        screen = self._get_screen(index)
        return screen.availableGeometry() if screen else None

    def is_raspberry_pi(self) -> bool:
        """Check whether the hardware is a Raspberry Pi.

        Returns
        -------
        bool
            True on Linux when ``/proc/device-tree/model`` contains
            "raspberry pi" (any case); False otherwise or on read
            errors.
        """
        if not sys.platform.startswith("lin"):
            return False
        try:
            if os.path.exists("/proc/device-tree/model"):
                with open("/proc/device-tree/model", "r") as f:
                    return "raspberry pi" in f.read().lower()
            return False
        except Exception:
            return False

    def is_windows(self) -> bool:
        """Check whether the operating system is Windows.

        Returns
        -------
        bool
            True if ``sys.platform`` starts with ``"win"``.
        """
        return sys.platform.startswith("win")

    def create_calibration_hardware(
        self, data: Dict[str, Any]
    ) -> Optional[Calibration]:
        """Save the hardware calibration built from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``Calibration`` field.

        Returns
        -------
        int | None
            ``Calibration.ID_VALUE`` (the ID returned by the DAO), or
            None if the calibration is not valid. The ``Calibration |
            None`` annotation does not match this.

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.
        """
        calibration = Calibration(**data)
        calibration.set_data(data)

        if not calibration.is_valid():
            return None

        return self.dao.insert(calibration)

    def find_by_id_calibration(
        self, calibration_id: int
    ) -> Optional[Calibration]:
        """Return the saved hardware calibration.

        Parameters
        ----------
        calibration_id : int
            Ignored by the INI DAO: there is only one record.

        Returns
        -------
        Calibration | None
            The calibration, or None if no camera is saved.
        """
        return self.dao.select(calibration_id)

    def create_calibration_point(
        self, data: Dict[str, Any]
    ) -> Optional[CalibrationPoint]:
        """Save the calibration points built from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``CalibrationPoint`` field
            (``pointx1``...``pointy4``).

        Returns
        -------
        CalibrationPoint | None
            The saved points read back from the cache.

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.
        """
        calibration_point = CalibrationPoint(**data)

        new_id = self.dao_calibration_point.insert(calibration_point)
        return (
            self.dao_calibration_point.select(new_id) if new_id > 0 else None
        )

    def find_by_id_calibration_point(
        self, calibration_point_id: int
    ) -> Optional[CalibrationPoint]:
        """Return the saved calibration points.

        Parameters
        ----------
        calibration_point_id : int
            Record ID, normally ``CalibrationPoint.ID_VALUE``.

        Returns
        -------
        CalibrationPoint | None
            The points, or None if none were saved.
        """
        return self.dao_calibration_point.select(calibration_point_id)

    # ======================
    # Hardware
    # ======================
    def is_fullscreen(self) -> bool:
        """Check whether the default calibration opens in full screen.

        Returns
        -------
        bool
            True if ``get_window_open_mode()`` of the settings service
            is ``CalibrationSetting.FULLSCREEN``.
        """
        if (
            self.calibration_setting_service.get_window_open_mode()
            == CalibrationSetting.FULLSCREEN
        ):
            return True
        else:
            return False

    def get_screen_size(self) -> Optional[Dict[str, int]]:
        """Return the window size for the default calibration mode.

        Returns
        -------
        dict[str, int] | None
            ``{"width": ..., "height": ...}``: the screen size for
            ``FULLSCREEN`` and ``MAXIMIZED``, the available screen size
            for ``MAXIMIZED_UTIL``. None if there is no saved
            calibration or the mode is none of these.
        """
        value = self.calibration_setting_service.get_window_open_mode()
        calibration = self.dao.select(Calibration.ID_VALUE)

        if calibration is None:
            return None
        else:
            if value == CalibrationSetting.FULLSCREEN:
                return {
                    "width": calibration.screen_width,
                    "height": calibration.screen_height,
                }
            elif value == CalibrationSetting.MAXIMIZED:
                return {
                    "width": calibration.screen_width,
                    "height": calibration.screen_height,
                }
            elif value == CalibrationSetting.MAXIMIZED_UTIL:
                return {
                    "width": calibration.screen_available_width,
                    "height": calibration.screen_available_height,
                }

    def get_camera_info(self) -> Optional[Dict[str, int]]:
        """Return the camera fields of the saved calibration.

        Returns
        -------
        dict[str, Any] | None
            The ``camera_*`` fields by name, or None if there is no
            saved calibration.
        """
        calibration = self.dao.select(Calibration.ID_VALUE)

        if calibration is None:
            return None
        else:
            return {
                "camera_description": calibration.camera_description,
                "camera_id": calibration.camera_id,
                "camera_position": calibration.camera_position,
                "camera_width": calibration.camera_width,
                "camera_height": calibration.camera_height,
                "camera_max_fps": calibration.camera_max_fps,
                "camera_min_fps": calibration.camera_min_fps,
            }

    def get_screen_info(self) -> Optional[Dict[str, int]]:
        """Return the screen fields of the saved calibration.

        Returns
        -------
        dict[str, Any] | None
            The ``screen_*`` fields by name, or None if there is no
            saved calibration.
        """
        calibration = self.dao.select(Calibration.ID_VALUE)

        if calibration is None:
            return None
        else:
            return {
                "screen_manufacturer": calibration.screen_manufacturer,
                "screen_model": calibration.screen_model,
                "screen_position": calibration.screen_position,
                "screen_serial_number": calibration.screen_serial_number,
                "screen_width": calibration.screen_width,
                "screen_height": calibration.screen_height,
                "screen_available_width": calibration.screen_available_width,
                "screen_available_height": calibration.screen_available_height,
                "screen_pos_x": calibration.screen_pos_x,
                "screen_pos_y": calibration.screen_pos_y,
            }

    # ======================
    # MEDIAPIPE
    # ======================

    def get_mediapipe_model_desktop(self) -> str:
        """Return the MediaPipe model file name for desktop systems.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_mediapipe_model_desktop()

    def get_mediapipe_model_embedded(self) -> str:
        """Return the MediaPipe model file name for embedded systems.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_mediapipe_model_embedded()

    def get_mediapipe_embedded_processing(self) -> str:
        """Return the MediaPipe processing option for embedded systems.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_embedded_processing()
        )

    def get_mediapipe_linux_processing(self) -> str:
        """Return the MediaPipe processing option for Linux.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_linux_processing()
        )

    def get_mediapipe_mac_processing(self) -> str:
        """Return the MediaPipe processing option for macOS.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_mediapipe_mac_processing()

    def get_mediapipe_windows_processing(self) -> str:
        """Return the MediaPipe processing option for Windows.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_windows_processing()
        )

    def get_mediapipe_execution_mode(self) -> any:
        """Return the MediaPipe running mode.

        Returns
        -------
        vision.RunningMode
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_mediapipe_execution_mode()

    def is_enable_mediapipe_pose(self) -> bool:
        """Check whether pose detection is enabled.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``
            (``is_mediapipe_enable_pose``).
        """
        return self.calibration_setting_service.is_mediapipe_enable_pose()

    def get_mediapipe_detection_position(self) -> float:
        """Return the minimum pose detection confidence.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_detection_position()
        )

    def get_mediapipe_detection_presence(self) -> float:
        """Return the minimum pose presence confidence.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_detection_presence()
        )

    def get_mediapipe_detection_tracking(self) -> float:
        """Return the minimum pose tracking confidence.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_mediapipe_detection_tracking()
        )

    def get_mediapipe_num_position(self) -> int:
        """Return the maximum number of poses detected.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_mediapipe_num_position()

    # ======================
    # OPENCV
    # ======================

    def get_opencv_capture_backend(self) -> int:
        """Return the OpenCV capture backend for the current platform.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_capture_backend()

    def get_opencv_buffer_size(self) -> int:
        """Return the camera capture buffer size.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_buffer_size()

    def is_opencv_custom_camera(self) -> int:
        """Check whether a custom camera is used.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_opencv_custom_camera()

    def get_opencv_ratio(self) -> str:
        """Return the capture aspect ratio name.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_ratio()

    def get_opencv_width(self) -> int:
        """Return the capture width in pixels.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_width()

    def get_opencv_height(self) -> int:
        """Return the capture height in pixels.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_height()

    def get_opencv_fps(self) -> int:
        """Return the capture frame rate.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_opencv_fps()

    # ======================
    # FILTER
    # ======================

    def is_filter_enable_filter(self) -> int:
        """Check whether image enhancement is enabled.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_filter_enable_filter()

    def get_filter_average_smooth_frames(self) -> int:
        """Return the number of frames averaged per landmark.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_filter_average_smooth_frames()
        )

    def get_filter_clahe_clip(self) -> int:
        """Return the CLAHE clip limit.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_clahe_clip()

    def get_filter_clahe_grid(self) -> tuple[int, int]:
        """Return the CLAHE tile grid size.

        Returns
        -------
        tuple[int, ...]
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_clahe_grid()

    def get_filter_clahe_lum_below(self) -> int:
        """Return the brightness (0-255) below which CLAHE runs.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_clahe_lum_below()

    def get_filter_gamma_factor(self) -> float:
        """Return the gamma correction factor.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_gamma_factor()

    def get_filter_gamma_lum_above(self) -> int:
        """Return the brightness (0-255) above which gamma runs.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_gamma_lum_above()

    def get_filter_landmark_limit(self) -> float:
        """Return the landmark jump that resets its smoothing.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_filter_landmark_limit()

    # ======================
    # TELEMETRY
    # ======================
    def is_telemetry_enable_panel(self) -> bool:
        """Check whether the telemetry panel is shown.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_telemetry_enable_panel()

    # ======================
    # AUTOMATIC CALIBRATION
    # ======================

    def get_automatic_window_position(self) -> str:
        """Return the window position of the automatic mode.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_window_position()

    def get_automatic_window_open_mode(self) -> int:
        """Return the window display mode of the automatic mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_automatic_window_open_mode()
        )

    def is_automatic_open_projector(self) -> bool:
        """Return the the open-projector flag of the automatic mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_automatic_open_projector()

    def is_automatic_default_calibration(self) -> bool:
        """Check whether the automatic mode is the default.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.is_automatic_default_calibration()
        )

    def is_automatic_mirror_mode(self) -> bool:
        """Check whether the automatic mode mirrors the image.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_automatic_mirror_mode()

    def get_automatic_num_columns(self) -> int:
        """Return the column count of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_num_columns()

    def get_automatic_num_rows(self) -> int:
        """Return the row count of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_num_rows()

    def get_automatic_multiplier(self) -> int:
        """Return the multiplier of the automatic calibration.

        Returns
        -------
        float
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_multiplier()

    def get_automatic_dictionary(self) -> int:
        """Return the ArUco dictionary of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_dictionary()

    def get_automatic_width(self) -> int:
        """Return the width of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_width()

    def get_automatic_height(self) -> int:
        """Return the height of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_height()

    def get_automatic_margin(self) -> int:
        """Return the margin of the calibration pattern.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_automatic_margin()

    # ======================
    # SEMIAUTOMATIC CALIBRATION
    # ======================

    def get_semiautomatic_window_position(self) -> str:
        """Return the window position of the semiautomatic mode.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_semiautomatic_window_position()
        )

    def get_semiautomatic_window_open_mode(self) -> int:
        """Return the window display mode of the semiautomatic mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.get_semiautomatic_window_open_mode()
        )

    def is_semiautomatic_open_projector(self) -> bool:
        """Return the the open-projector flag of the semiautomatic mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.is_semiautomatic_open_projector()
        )

    def is_semiautomatic_default_calibration(self) -> bool:
        """Check whether the semiautomatic mode is the default.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return (
            self.calibration_setting_service.is_semiautomatic_default_calibration()
        )

    def is_semiautomatic_mirror_mode(self) -> bool:
        """Check whether the semiautomatic mode mirrors the image.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_semiautomatic_mirror_mode()

    # ======================
    # MANUAL CALIBRATION
    # ======================

    def get_manual_window_position(self) -> str:
        """Return the window position of the manual mode.

        Returns
        -------
        str
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_manual_window_position()

    def get_manual_window_open_mode(self) -> int:
        """Return the window display mode of the manual mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.get_manual_window_open_mode()

    def is_manual_open_projector(self) -> bool:
        """Return the the open-projector flag of the manual mode.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_manual_open_projector()

    def is_manual_default_calibration(self) -> bool:
        """Check whether the manual mode is the default.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_manual_default_calibration()

    def is_manual_mirror_mode(self) -> bool:
        """Check whether the manual mode mirrors the image.

        Returns
        -------
        int
            Value from ``CalibrationSettingService``.
        """
        return self.calibration_setting_service.is_manual_mirror_mode()
