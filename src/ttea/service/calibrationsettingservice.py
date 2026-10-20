"""Access to the calibration settings (MediaPipe, OpenCV, filters...).

Reads each tuning parameter from the calibration settings INI file, with
a default value and a type conversion per setting.
"""

import sys
from typing import TYPE_CHECKING, Any, Dict, Optional

import cv2
from mediapipe.tasks.python import vision
from PySide6.QtCore import QSettings

from ttea.dao import CalibrationSettingIniDAO
from ttea.model import CalibrationSetting
from ttea.util import PathConfig

if TYPE_CHECKING:
    from ttea.service import CalibrationService


class CalibrationSettingService:
    """Read and save the calibration settings.

    Parameters
    ----------
    dao : CalibrationSettingIniDAO | None, optional
        DAO used to save the settings record. Default is None, which
        creates a new ``CalibrationSettingIniDAO``.
    calibration_service : CalibrationService | None, optional
        Calibration service to reuse. Default is None, which creates one
        on first use (see ``calibration_service``).

    Attributes
    ----------
    settings : QSettings
        INI file at ``PathConfig.calibration_setting()``, read by the
        getters.
    dao : CalibrationSettingIniDAO
        DAO used to save the settings record.

    Notes
    -----
    Each getter reads its key from ``settings`` on every call, so
    changes saved by the DAO are seen immediately. Values are read as
    text, stripped and converted; a value that cannot be converted
    raises ``ValueError``.

    The ``is_*`` getters return the ``int`` value of the setting (0 or 1
    in practice), not a ``bool``.
    """

    def __init__(
        self,
        dao: Optional[CalibrationSettingIniDAO] = None,
        calibration_service: Optional["CalibrationService"] = None,
    ):

        self.settings = QSettings(
            PathConfig.calibration_setting(), QSettings.IniFormat
        )
        self.dao = dao or CalibrationSettingIniDAO()
        self._calibration_service = calibration_service

    @property
    def calibration_service(self):
        """Calibration service, created on first use if not injected."""
        if self._calibration_service is None:
            from ttea.service import CalibrationService

            self._calibration_service = CalibrationService(
                calibration_setting_service=self
            )
        return self._calibration_service

    def create_calibration_setting(
        self, data: Dict[str, Any]
    ) -> Optional[CalibrationSetting]:
        """Save a settings record built from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Values for every ``CalibrationSetting`` field.

        Returns
        -------
        CalibrationSetting | None
            The record read back from the INI file, or None if it is not
            valid (a field is None).

        Raises
        ------
        TypeError
            If ``data`` misses a field or has an unknown key.
        """
        calibration_setting = CalibrationSetting(**data)

        new_id = self.dao.insert(calibration_setting)
        return self.dao.select(new_id) if new_id > 0 else None

    def get_proportions(self) -> Dict[str, tuple[int, int]]:
        """Return the supported aspect ratios.

        Returns
        -------
        dict_items
            ``CalibrationSetting.PROPORTIONS.items()``: pairs of name
            (e.g. ``"16:9"``) and ``(width, height)``, despite the
            ``dict`` annotation.
        """
        return CalibrationSetting.PROPORTIONS.items()

    def is_raspberry_pi(self) -> bool:
        """Check whether the hardware is a Raspberry Pi.

        Returns
        -------
        bool
            Result of ``CalibrationService.is_raspberry_pi()``.
        """
        return self.calibration_service.is_raspberry_pi()

    def get_window_open_mode(self) -> int:
        """Return the window display mode of the default calibration.

        Returns
        -------
        int
            The ``*_window_open_*`` setting of the first calibration
            (automatic, semiautomatic, manual) flagged as default, or 1
            (``CalibrationSetting.FULLSCREEN``) if none is.
        """
        if self.is_automatic_default_calibration():
            return self.get_automatic_window_open_mode()
        elif self.is_semiautomatic_default_calibration():
            return self.get_semiautomatic_window_open_mode()
        elif self.is_manual_default_calibration():
            return self.get_manual_window_open_mode()
        else:
            return 1

    # ======================
    # MEDIAPIPE
    # ======================

    def get_mediapipe_model_desktop(self) -> str:
        """Return the MediaPipe model file name for desktop systems.

        Returns
        -------
        str
            Setting ``mediapipe_model_desktop`` of section
            ``[mediapipe]`` (default ``"pose_landmarker_full.task"``),
            stripped and lowercased.
        """
        return str(
            self.settings.value(
                "mediapipe/mediapipe_model_desktop",
                "pose_landmarker_full.task",
            )
            .strip()
            .lower()
        )

    def get_mediapipe_model_embedded(self) -> str:
        """Return the MediaPipe model file name for embedded systems.

        Returns
        -------
        str
            Setting ``mediapipe_model_embedded`` of section
            ``[mediapipe]`` (default ``"pose_landmarker_lite.task"``),
            stripped and lowercased.
        """
        return str(
            self.settings.value(
                "mediapipe/mediapipe_model_embedded",
                "pose_landmarker_lite.task",
            )
            .strip()
            .lower()
        )

    def get_mediapipe_embedded_processing(self) -> str:
        """Return the MediaPipe processing option for embedded systems.

        Returns
        -------
        str
            Setting ``mediapipe_embedded_processing`` of section
            ``[mediapipe]`` (default ``"cpu"``), stripped and
            lowercased.
        """
        return str(
            self.settings.value(
                "mediapipe/mediapipe_embedded_processing", "cpu"
            )
            .strip()
            .lower()
        )

    def get_mediapipe_linux_processing(self) -> str:
        """Return the MediaPipe processing option for Linux.

        Returns
        -------
        str
            Setting ``mediapipe_linux_processing`` of section
            ``[mediapipe]`` (default ``"cpu"``), stripped and
            lowercased.
        """
        return str(
            self.settings.value("mediapipe/mediapipe_linux_processing", "cpu")
            .strip()
            .lower()
        )

    def get_mediapipe_mac_processing(self) -> str:
        """Return the MediaPipe processing option for macOS.

        Returns
        -------
        str
            Setting ``mediapipe_mac_processing`` of section
            ``[mediapipe]`` (default ``"cpu"``), stripped and
            lowercased.
        """
        return str(
            self.settings.value("mediapipe/mediapipe_mac_processing", "cpu")
            .strip()
            .lower()
        )

    def get_mediapipe_windows_processing(self) -> str:
        """Return the MediaPipe processing option for Windows.

        Returns
        -------
        str
            Setting ``mediapipe_windows_processing`` of section
            ``[mediapipe]`` (default ``"cpu"``), stripped and
            lowercased.
        """
        return str(
            self.settings.value(
                "mediapipe/mediapipe_windows_processing", "cpu"
            )
            .strip()
            .lower()
        )

    def get_mediapipe_execution_mode(self) -> any:
        """Return the MediaPipe running mode.

        Returns
        -------
        vision.RunningMode
            Always ``vision.RunningMode.VIDEO`` at present.

        Notes
        -----
        The code looks up ``"vision.RunningMode.<value>"`` (value of
        ``mediapipe/mediapipe_execution_mode``, default ``"VIDEO"``) as
        an attribute of ``cv2``. No such attribute exists, so the
        fallback ``vision.RunningMode.VIDEO`` is always returned and the
        setting has no effect.
        """
        value = "vision.RunningMode." + str(
            self.settings.value(
                "mediapipe/mediapipe_execution_mode", "VIDEO"
            ).strip()
        )

        return getattr(cv2, value, vision.RunningMode.VIDEO)

    def is_mediapipe_enable_pose(self) -> bool:
        """Check whether pose detection is enabled.

        Returns
        -------
        int
            Setting ``mediapipe_enable_mediapipe_pose`` of section
            ``[mediapipe]`` (default ``"1"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value(
                "mediapipe/mediapipe_enable_mediapipe_pose", "1"
            )
        ).strip()

        return int(value)

    def get_mediapipe_detection_position(self) -> float:
        """Return the minimum pose detection confidence.

        Returns
        -------
        float
            Setting ``mediapipe_detection_position`` of section
            ``[mediapipe]`` (default ``"0.5"``), converted to ``float``.
        """
        value = str(
            self.settings.value(
                "mediapipe/mediapipe_detection_position", "0.5"
            )
        ).strip()

        return float(value)

    def get_mediapipe_detection_presence(self) -> float:
        """Return the minimum pose presence confidence.

        Returns
        -------
        float
            Setting ``mediapipe_detection_presence`` of section
            ``[mediapipe]`` (default ``"0.5"``), converted to ``float``.
        """
        value = str(
            self.settings.value(
                "mediapipe/mediapipe_detection_presence", "0.5"
            )
        ).strip()

        return float(value)

    def get_mediapipe_detection_tracking(self) -> float:
        """Return the minimum pose tracking confidence.

        Returns
        -------
        float
            Setting ``mediapipe_detection_tracking`` of section
            ``[mediapipe]`` (default ``"0.5"``), converted to ``float``.
        """
        value = str(
            self.settings.value(
                "mediapipe/mediapipe_detection_tracking", "0.5"
            )
        ).strip()

        return float(value)

    def get_mediapipe_num_position(self) -> int:
        """Return the maximum number of poses detected.

        Returns
        -------
        int
            Setting ``mediapipe_num_position`` of section
            ``[mediapipe]`` (default ``"1"``), converted to ``int``.
        """
        value = str(
            self.settings.value("mediapipe/mediapipe_num_position", "1")
        ).strip()

        return int(value)

    # ======================
    # OPENCV
    # ======================

    def get_opencv_capture_backend(self) -> int:
        """Return the OpenCV capture backend for the current platform.

        Returns
        -------
        int
            The ``cv2`` constant named by the setting (e.g.
            ``"CAP_DSHOW"``), or ``cv2.CAP_ANY`` if the name is missing
            or unknown.

        Notes
        -----
        The key depends on the platform:
        ``opencv/opencv_windows_capture`` on Windows,
        ``opencv/opencv_mac_capture`` on macOS,
        ``opencv/opencv_embedded_capture`` on a Raspberry Pi and
        ``opencv/opencv_linux_capture`` on other systems.
        """
        if sys.platform.startswith("win"):
            key_name = "opencv/opencv_windows_capture"
        elif sys.platform.startswith("darwin"):
            key_name = "opencv/opencv_mac_capture"
        elif self.is_raspberry_pi():
            key_name = "opencv/opencv_embedded_capture"
        else:  # other Linux systems
            key_name = "opencv/opencv_linux_capture"

        value = str(self.settings.value(key_name, "CAP_ANY")).strip()

        return getattr(cv2, value, cv2.CAP_ANY)

    def get_opencv_buffer_size(self) -> int:
        """Return the camera capture buffer size.

        Returns
        -------
        int
            Setting ``opencv_buffer_size`` of section ``[opencv]``
            (default ``"1"``), converted to ``int``.
        """
        value = str(
            self.settings.value("opencv/opencv_buffer_size", "1")
        ).strip()

        return int(value)

    def is_opencv_custom_camera(self) -> int:
        """Check whether a custom camera is used.

        Returns
        -------
        int
            Setting ``opencv_custom_camera`` of section ``[opencv]``
            (default ``"0"``), converted to ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value("opencv/opencv_custom_camera", "0")
        ).strip()

        return int(value)

    def get_opencv_ratio(self) -> str:
        """Return the capture aspect ratio name.

        Returns
        -------
        str
            Setting ``opencv_ratio`` of section ``[opencv]``, stripped;
            ``"None"`` when the key is missing.
        """
        value = str(self.settings.value("opencv/opencv_ratio")).strip()

        return value

    def get_opencv_width(self) -> int:
        """Return the capture width in pixels.

        Returns
        -------
        int
            Setting ``opencv_width`` of section ``[opencv]`` (default
            ``"640"``), converted to ``int``.
        """
        value = str(self.settings.value("opencv/opencv_width", "640")).strip()

        return int(value)

    def get_opencv_height(self) -> int:
        """Return the capture height in pixels.

        Returns
        -------
        int
            Setting ``opencv_height`` of section ``[opencv]`` (default
            ``"480"``), converted to ``int``.
        """
        value = str(self.settings.value("opencv/opencv_height", "480")).strip()

        return int(value)

    def get_opencv_fps(self) -> int:
        """Return the capture frame rate.

        Returns
        -------
        int
            Setting ``opencv_fps`` of section ``[opencv]`` (default
            ``"30"``), converted to ``int``.
        """
        value = str(self.settings.value("opencv/opencv_fps", "30")).strip()

        return int(value)

    # ======================
    # FILTER
    # ======================
    def is_filter_enable_filter(self) -> int:
        """Check whether image enhancement is enabled.

        Returns
        -------
        int
            Setting ``filter_enable_filter`` of section ``[filter]``
            (default ``"0"``), converted to ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value("filter/filter_enable_filter", "0")
        ).strip()

        return int(value)

    def get_filter_average_smooth_frames(self) -> int:
        """Return the number of frames averaged per landmark.

        Returns
        -------
        int
            Setting ``filter_average_smooth_frames`` of section
            ``[filter]`` (default ``"5"``), converted to ``int``.
        """
        value = str(
            self.settings.value("filter/filter_average_smooth_frames", "5")
        ).strip()

        return int(value)

    def get_filter_clahe_clip(self) -> int:
        """Return the CLAHE clip limit.

        Returns
        -------
        int
            Setting ``filter_clahe_clip`` of section ``[filter]``
            (default ``"2"``), converted to ``int``.
        """
        value = str(
            self.settings.value("filter/filter_clahe_clip", "2")
        ).strip()

        return int(value)

    def get_filter_clahe_grid(self) -> tuple[int, int]:
        """Return the CLAHE tile grid size.

        Returns
        -------
        tuple[int, ...]
            Setting ``filter_clahe_grid`` of section ``[filter]``
            (default ``"8:8"``), the ``"x:y"`` text split on ``":"`` and
            converted to ints.
        """
        value = str(
            self.settings.value("filter/filter_clahe_grid", "8:8")
        ).strip()

        grid = tuple(map(int, value.split(":")))

        return grid

    def get_filter_clahe_lum_below(self) -> int:
        """Return the brightness (0-255) below which CLAHE runs.

        Returns
        -------
        int
            Setting ``filter_clahe_lum_below`` of section ``[filter]``
            (default ``"100"``), converted to ``int``.
        """
        value = str(
            self.settings.value("filter/filter_clahe_lum_below", "100")
        ).strip()

        return int(value)

    def get_filter_gamma_factor(self) -> float:
        """Return the gamma correction factor.

        Returns
        -------
        float
            Setting ``filter_gamma_factor`` of section ``[filter]``
            (default ``"1.2"``), converted to ``float``.
        """
        value = str(
            self.settings.value("filter/filter_gamma_factor", "1.2")
        ).strip()

        return float(value)

    def get_filter_gamma_lum_above(self) -> int:
        """Return the brightness (0-255) above which gamma runs.

        Returns
        -------
        int
            Setting ``filter_gamma_lum_above`` of section ``[filter]``
            (default ``"100"``), converted to ``int``.
        """
        value = str(
            self.settings.value("filter/filter_gamma_lum_above", "100")
        ).strip()

        return int(value)

    def get_filter_landmark_limit(self) -> float:
        """Return the landmark jump that resets its smoothing.

        Returns
        -------
        float
            Setting ``filter_landmark_limit`` of section ``[filter]``
            (default ``"0.15"``), converted to ``float``.
        """
        value = str(
            self.settings.value("filter/filter_landmark_limit", "0.15")
        ).strip()

        return float(value)

    # ======================
    # TELEMETRY
    # ======================
    def is_telemetry_enable_panel(self) -> bool:
        """Check whether the telemetry panel is shown.

        Returns
        -------
        int
            Setting ``telemetry_enable_telemetry_panel`` of section
            ``[telemetry]`` (default ``"1"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value(
                "telemetry/telemetry_enable_telemetry_panel", "1"
            )
        ).strip()

        return int(value)

    # ======================
    # AUTOMATIC CALIBRATION
    # ======================
    def get_automatic_window_position(self) -> str:
        """Return the window position of the automatic mode.

        Returns
        -------
        str
            Setting ``automatic_window_position_automatic`` of section
            ``[automatic]``, stripped; ``"None"`` when the key is
            missing.
        """
        key_name = "automatic/automatic_window_position_automatic"

        method_name = str(
            self.settings.value(
                key_name,
            )
        ).strip()

        return method_name

    def get_automatic_window_open_mode(self) -> int:
        """Return the window display mode of the automatic mode.

        Returns
        -------
        int
            Setting ``automatic_window_open_automatic`` of section
            ``[automatic]`` (default ``"1"``), converted to ``int``.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_window_open_automatic", "1"
            )
        ).strip()

        return int(value)

    def is_automatic_open_projector(self) -> bool:
        """Return the the open-projector flag of the automatic mode.

        Returns
        -------
        int
            Setting ``automatic_open_projector_automatic`` of section
            ``[automatic]`` (default ``"0"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_open_projector_automatic", "0"
            )
        ).strip()

        return int(value)

    def is_automatic_default_calibration(self) -> bool:
        """Check whether the automatic mode is the default.

        Returns
        -------
        int
            Setting ``automatic_default_calibration_automatic`` of
            section ``[automatic]`` (default ``"0"``), converted to
            ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_default_calibration_automatic", "0"
            )
        ).strip()

        return int(value)

    def is_automatic_mirror_mode(self) -> bool:
        """Check whether the automatic mode mirrors the image.

        Returns
        -------
        int
            Setting ``automatic_mirror_mode_automatic`` of section
            ``[automatic]`` (default ``"1"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_mirror_mode_automatic", "1"
            )
        ).strip()

        return int(value)

    def get_automatic_num_columns(self) -> int:
        """Return the column count of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_num_columns_automatic`` of section
            ``[automatic]`` (default ``"6"``), converted to ``int``.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_num_columns_automatic", "6"
            )
        ).strip()

        return int(value)

    def get_automatic_num_rows(self) -> int:
        """Return the row count of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_num_rows_automatic`` of section
            ``[automatic]`` (default ``"4"``), converted to ``int``.
        """
        value = str(
            self.settings.value("automatic/automatic_num_rows_automatic", "4")
        ).strip()

        return int(value)

    def get_automatic_multiplier(self) -> float:
        """Return the multiplier of the automatic calibration.

        Returns
        -------
        float
            Setting ``automatic_multiplier_automatic`` of section
            ``[automatic]`` (default ``"0.75"``), converted to
            ``float``.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_multiplier_automatic", "0.75"
            )
        ).strip()

        return float(value)

    def get_automatic_dictionary(self) -> int:
        """Return the ArUco dictionary of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_dictionary_automatic`` of section
            ``[automatic]`` (default ``"DICT_4X4_250"``), the
            ``cv2.aruco`` constant named by the setting;
            ``cv2.aruco.DICT_4X4_250`` if the name is unknown.
        """
        value = str(
            self.settings.value(
                "automatic/automatic_dictionary_automatic", "DICT_4X4_250"
            )
        ).strip()

        return getattr(cv2.aruco, value, cv2.aruco.DICT_4X4_250)

    def get_automatic_width(self) -> int:
        """Return the width of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_width_automatic`` of section
            ``[automatic]`` (default ``"100"``), converted to ``int``.
        """
        value = str(
            self.settings.value("automatic/automatic_width_automatic", "100")
        ).strip()

        return int(value)

    def get_automatic_height(self) -> int:
        """Return the height of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_height_automatic`` of section
            ``[automatic]`` (default ``"100"``), converted to ``int``.
        """
        value = str(
            self.settings.value("automatic/automatic_height_automatic", "100")
        ).strip()

        return int(value)

    def get_automatic_margin(self) -> int:
        """Return the margin of the calibration pattern.

        Returns
        -------
        int
            Setting ``automatic_margin_automatic`` of section
            ``[automatic]`` (default ``"0"``), converted to ``int``.
        """
        value = str(
            self.settings.value("automatic/automatic_margin_automatic", "0")
        ).strip()

        return int(value)

    # ======================
    # SEMIAUTOMATIC CALIBRATION
    # ======================

    def get_semiautomatic_window_position(self) -> str:
        """Return the window position of the semiautomatic mode.

        Returns
        -------
        str
            Setting ``semiautomatic_window_position_semiautomatic`` of
            section ``[semiautomatic]``, stripped; ``"None"`` when the
            key is missing.
        """
        key_name = "semiautomatic/semiautomatic_window_position_semiautomatic"

        method_name = str(
            self.settings.value(
                key_name,
            )
        ).strip()

        return method_name

    def get_semiautomatic_window_open_mode(self) -> int:
        """Return the window display mode of the semiautomatic mode.

        Returns
        -------
        int
            Setting ``semiautomatic_window_open_semiautomatic`` of
            section ``[semiautomatic]`` (default ``"1"``), converted to
            ``int``.
        """
        value = str(
            self.settings.value(
                "semiautomatic/semiautomatic_window_open_semiautomatic", "1"
            )
        ).strip()

        return int(value)

    def is_semiautomatic_open_projector(self) -> bool:
        """Return the the open-projector flag of the semiautomatic mode.

        Returns
        -------
        int
            Setting ``semiautomatic_open_projector_semiautomatic`` of
            section ``[semiautomatic]`` (default ``"0"``), converted to
            ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value(
                "semiautomatic/semiautomatic_open_projector_semiautomatic", "0"
            )
        ).strip()

        return int(value)

    def is_semiautomatic_default_calibration(self) -> bool:
        """Check whether the semiautomatic mode is the default.

        Returns
        -------
        int
            Setting ``semiautomatic_default_calibration_semiautomatic``
            of section ``[semiautomatic]`` (default ``"0"``), converted
            to ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value(
                "semiautomatic/semiautomatic_default_calibration_semiautomatic",
                "0",
            )
        ).strip()

        return int(value)

    def is_semiautomatic_mirror_mode(self) -> bool:
        """Check whether the semiautomatic mode mirrors the image.

        Returns
        -------
        int
            Setting ``semiautomatic_mirror_mode_semiautomatic`` of
            section ``[semiautomatic]`` (default ``"1"``), converted to
            ``int``: non-zero means yes.
        """
        value = str(
            self.settings.value(
                "semiautomatic/semiautomatic_mirror_mode_semiautomatic", "1"
            )
        ).strip()

        return int(value)

    # ======================
    # MANUAL CALIBRATION
    # ======================

    def get_manual_window_position(self) -> str:
        """Return the window position of the manual mode.

        Returns
        -------
        str
            Setting ``manual_window_position_manual`` of section
            ``[manual]``, stripped; ``"None"`` when the key is missing.
        """
        key_name = "manual/manual_window_position_manual"

        method_name = str(
            self.settings.value(
                key_name,
            )
        ).strip()

        return method_name

    def get_manual_window_open_mode(self) -> int:
        """Return the window display mode of the manual mode.

        Returns
        -------
        int
            Setting ``manual_window_open_manual`` of section
            ``[manual]`` (default ``"1"``), converted to ``int``.
        """
        value = str(
            self.settings.value("manual/manual_window_open_manual", "1")
        ).strip()

        return int(value)

    def is_manual_open_projector(self) -> bool:
        """Return the the open-projector flag of the manual mode.

        Returns
        -------
        int
            Setting ``manual_open_projector_manual`` of section
            ``[manual]`` (default ``"0"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value("manual/manual_open_projector_manual", "0")
        ).strip()

        return int(value)

    def is_manual_default_calibration(self) -> bool:
        """Check whether the manual mode is the default.

        Returns
        -------
        int
            Setting ``manual_default_calibration_manual`` of section
            ``[manual]`` (default ``"0"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value(
                "manual/manual_default_calibration_manual", "0"
            )
        ).strip()

        return int(value)

    def is_manual_mirror_mode(self) -> bool:
        """Check whether the manual mode mirrors the image.

        Returns
        -------
        int
            Setting ``manual_mirror_mode_manual`` of section
            ``[manual]`` (default ``"1"``), converted to ``int``:
            non-zero means yes.
        """
        value = str(
            self.settings.value("manual/manual_mirror_mode_manual", "1")
        ).strip()

        return int(value)
