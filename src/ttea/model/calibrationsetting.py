"""Calibration settings model: MediaPipe, OpenCV, filters and windows.

Holds the tuning parameters saved in the calibration settings .ini
file (one record, see ``ID_VALUE``). Each field prefix is an .ini
section (see ``SECTIONS_MAP``).
"""

from dataclasses import dataclass, fields
from typing import ClassVar, Dict, List


def initialize_reflexive(cls):
    """Fill the reflection lists of a dataclass (class decorator).

    Parameters
    ----------
    cls : type
        Dataclass to decorate; it must already be a dataclass.

    Returns
    -------
    type
        The same class, with ``PROPERTIES`` and ``DATA_PROPERTIES``
        set.

    Notes
    -----
    ``PROPERTIES`` receives the names of the dataclass fields, in
    declaration order (``ClassVar`` names are not fields).
    ``DATA_PROPERTIES`` receives the default value of each ``init``
    field; a field without a default contributes
    ``dataclasses.MISSING``.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class CalibrationSetting:
    """Represent the calibration settings of the application.

    Attributes
    ----------
    mediapipe_model_desktop, mediapipe_model_embedded : str
        MediaPipe model file names for desktop and embedded systems.
    mediapipe_embedded_processing, mediapipe_linux_processing : str
        MediaPipe processing option for embedded systems and Linux.
    mediapipe_mac_processing, mediapipe_windows_processing : str
        MediaPipe processing option for macOS and Windows.
    mediapipe_execution_mode : str
        MediaPipe running mode.
    mediapipe_enable_mediapipe_pose : int
        Pose detection switch.
    mediapipe_detection_position : float
        Minimum pose detection confidence.
    mediapipe_detection_presence : float
        Minimum pose presence confidence.
    mediapipe_detection_tracking : float
        Minimum pose tracking confidence.
    mediapipe_num_position : int
        Maximum number of poses detected.
    opencv_embedded_capture, opencv_linux_capture : str
        OpenCV capture backend for embedded systems and Linux.
    opencv_mac_capture, opencv_windows_capture : str
        OpenCV capture backend for macOS and Windows.
    opencv_buffer_size : int
        Capture buffer size.
    opencv_custom_camera : int
        Custom camera switch.
    opencv_ratio : str
        Capture aspect ratio name.
    opencv_width, opencv_height, opencv_fps : int
        Capture resolution in pixels and frame rate.
    filter_enable_filter : int
        Image enhancement switch.
    filter_average_smooth_frames : int
        Frames averaged when smoothing landmarks.
    filter_clahe_clip : int
        CLAHE clip limit.
    filter_clahe_grid : str
        CLAHE tile grid size.
    filter_clahe_lum_below : int
        Brightness (0-255) below which CLAHE is applied.
    filter_gamma_factor : float
        Gamma correction factor.
    filter_gamma_lum_above : int
        Brightness (0-255) above which gamma correction is applied.
    filter_landmark_limit : float
        Landmark movement (normalized) that resets its smoothing.
    telemetry_enable_telemetry_panel : int
        Telemetry panel switch.
    automatic_window_position_automatic : str
        Window position of the automatic calibration.
    automatic_window_open_automatic : str
        Window opening setting of the automatic calibration.
    automatic_open_projector_automatic : int
        Projector opening flag of the automatic mode.
    automatic_default_calibration_automatic : int
        Default calibration flag of the automatic mode.
    automatic_mirror_mode_automatic : int
        Mirror mode flag of the automatic calibration.
    automatic_num_columns_automatic, automatic_num_rows_automatic : int
        Size of the calibration pattern grid.
    automatic_multiplier_automatic : float
        Multiplier used by the automatic calibration.
    automatic_dictionary_automatic : str
        Dictionary used by the automatic calibration pattern.
    automatic_width_automatic, automatic_height_automatic : int
        Size of the automatic calibration pattern.
    automatic_margin_automatic : int
        Margin of the automatic calibration pattern.
    semiautomatic_window_position_semiautomatic : str
        Window position of the semiautomatic calibration.
    semiautomatic_window_open_semiautomatic : str
        Window opening setting of the semiautomatic calibration.
    semiautomatic_open_projector_semiautomatic : int
        Projector opening flag of the semiautomatic mode.
    semiautomatic_default_calibration_semiautomatic : int
        Default calibration flag of the semiautomatic mode.
    semiautomatic_mirror_mode_semiautomatic : int
        Mirror mode flag of the semiautomatic mode.
    manual_window_position_manual : str
        Window position of the manual calibration.
    manual_window_open_manual : str
        Window opening setting of the manual calibration.
    manual_open_projector_manual : int
        Projector opening flag of the manual mode.
    manual_default_calibration_manual : int
        Default calibration flag of the manual mode.
    manual_mirror_mode_manual : int
        Mirror mode flag of the manual calibration.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.
    ID_VALUE : int, class attribute
        Fixed identifier of the single settings record (1).
    PROPORTIONS : dict[str, tuple[int, int]], class attribute
        Supported aspect ratios by name.
    FULLSCREEN, MAXIMIZED, MAXIMIZED_UTIL : int, class attribute
        Window display mode codes (1, 2 and 3).
    SECTIONS_MAP : dict[str, str], class attribute
        Field name prefix to .ini section.
    IGNORED_PROPERTIES : list[str], class attribute
        Class attribute names that must not be saved.

    Notes
    -----
    Every field is required by the constructor; there are no
    defaults.

    TODO(doc): confirm the meaning of the ``*_window_open_*`` and
    ``*_default_calibration_*`` fields and which field uses the
    window display mode codes.

    Examples
    --------
    >>> n = len(CalibrationSetting.PROPERTIES)
    >>> s = CalibrationSetting(*[None] * n)
    >>> s.get_section_for_property("filter_gamma_factor")
    'filter'
    >>> s.get_section_for_property("other")
    'geral'
    """

    mediapipe_model_desktop: str
    mediapipe_model_embedded: str
    mediapipe_embedded_processing: str
    mediapipe_linux_processing: str
    mediapipe_mac_processing: str
    mediapipe_windows_processing: str
    mediapipe_execution_mode: str
    mediapipe_enable_mediapipe_pose: int
    mediapipe_detection_position: float
    mediapipe_detection_presence: float
    mediapipe_detection_tracking: float
    mediapipe_num_position: int

    opencv_embedded_capture: str
    opencv_linux_capture: str
    opencv_mac_capture: str
    opencv_windows_capture: str
    opencv_buffer_size: int
    opencv_custom_camera: int
    opencv_ratio: str
    opencv_width: int
    opencv_height: int
    opencv_fps: int

    filter_enable_filter: int
    filter_average_smooth_frames: int
    filter_clahe_clip: int
    filter_clahe_grid: str
    filter_clahe_lum_below: int
    filter_gamma_factor: float
    filter_gamma_lum_above: int
    filter_landmark_limit: float

    telemetry_enable_telemetry_panel: int

    automatic_window_position_automatic: str
    automatic_window_open_automatic: str
    automatic_open_projector_automatic: int
    automatic_default_calibration_automatic: int
    automatic_mirror_mode_automatic: int
    automatic_num_columns_automatic: int
    automatic_num_rows_automatic: int
    automatic_multiplier_automatic: float
    automatic_dictionary_automatic: str
    automatic_width_automatic: int
    automatic_height_automatic: int
    automatic_margin_automatic: int

    semiautomatic_window_position_semiautomatic: str
    semiautomatic_window_open_semiautomatic: str
    semiautomatic_open_projector_semiautomatic: int
    semiautomatic_default_calibration_semiautomatic: int
    semiautomatic_mirror_mode_semiautomatic: int

    manual_window_position_manual: str
    manual_window_open_manual: str
    manual_open_projector_manual: int
    manual_default_calibration_manual: int
    manual_mirror_mode_manual: int

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    ID_VALUE: ClassVar[int] = 1
    PROPORTIONS: ClassVar[dict[str, tuple[int, int]]] = {
        "4:3": (4, 3),
        "16:9": (16, 9),
    }

    FULLSCREEN = 1
    MAXIMIZED = 2
    MAXIMIZED_UTIL = 3

    SECTIONS_MAP: ClassVar[dict[str, str]] = {
        "mediapipe_": "mediapipe",
        "opencv_": "opencv",
        "filter_": "filter",
        "telemetry_": "telemetry",
        "automatic_": "automatic",
        "semiautomatic_": "semiautomatic",
        "manual_": "manual",
    }

    IGNORED_PROPERTIES: ClassVar[list[str]] = [
        "PROPERTIES",
        "DATA_PROPERTIES",
        "FULLSCREEN",
        "ID_VALUE",
        "MAXIMIZED",
        "MAXIMIZED_UTIL",
        "PROPORTIONS",
        "SECTIONS_MAP",
    ]

    def is_valid(self) -> bool:
        """Check that no field is None.

        Returns
        -------
        bool
            False if any field of ``PROPERTIES`` is None, True
            otherwise.
        """
        for prop in self.PROPERTIES:
            value = getattr(self, prop)

            if value is None:
                return False

        return True

    def set_data(self, data: Dict) -> None:
        """Update the fields from a dictionary.

        Parameters
        ----------
        data : dict
            Values keyed by field name. Keys that are not fields are
            ignored, and fields missing from ``data`` keep their value.

        Notes
        -----
        No validation or type conversion is done.
        """
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        """Return the field values as a one-item list.

        Returns
        -------
        list[dict]
            A list with one dictionary that maps each name of
            ``PROPERTIES`` to its current value.
        """
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]

    def get_proportion_tuple(self, proportion: str) -> tuple[int, int]:
        """Return the ``(width, height)`` ratio of a proportion name.

        Parameters
        ----------
        proportion : str
            Proportion name, ``"4:3"`` or ``"16:9"``.

        Returns
        -------
        tuple[int, int]
            The ratio from ``PROPORTIONS``, or ``(0, 0)`` if the name is
            unknown.
        """
        return self.PROPORTIONS.get(proportion, (0, 0))

    def get_section_for_property(self, prop_name: str) -> str:
        """Return the .ini section of a field, based on its prefix.

        Parameters
        ----------
        prop_name : str
            Field name.

        Returns
        -------
        str
            Section from ``SECTIONS_MAP`` for the first matching prefix,
            or ``"geral"`` if no prefix matches.
        """
        for prefix, section in self.SECTIONS_MAP.items():
            if prop_name.startswith(prefix):
                return section
        return "geral"
