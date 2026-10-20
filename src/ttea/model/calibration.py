"""Calibration model: camera, screen and projection area data.

Holds the hardware calibration saved in the calibration .ini file
(one record, see ``ID_VALUE``).
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
class Calibration:
    """Camera, screen and projected content calibration data.

    Attributes
    ----------
    camera_description : str
        Camera description.
    camera_id : str
        Camera identifier.
    camera_position : int
        Camera position (index).
    camera_width, camera_height : int
        Camera resolution in pixels.
    camera_max_fps, camera_min_fps : int
        Camera frame rate range.
    screen_manufacturer, screen_model : str
        Manufacturer and model of the projection screen.
    screen_position : int
        Screen position (index).
    screen_serial_number : str
        Screen serial number.
    screen_width, screen_height : int
        Screen resolution in pixels.
    screen_available_width, screen_available_height : int
        Available screen area in pixels.
    screen_pos_x, screen_pos_y : int
        Screen position on the virtual desktop, in pixels.
    content_width, content_height : int
        Area available for the projection, in pixels.
    content_width_ratio, content_height_ratio : int
        Aspect ratio of the content, e.g. 16 and 9.
    content_proportion : str
        Aspect ratio name, ``"4:3"`` or ``"16:9"``.
    calibration_date, calibration_hour : str
        Date and time of the calibration.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.
    ID_VALUE : int, class attribute
        Fixed identifier of the single calibration record (1).
    PROPORTIONS : dict[str, tuple[int, int]], class attribute
        Supported aspect ratios by name.
    SECTIONS_MAP : dict[str, str], class attribute
        Field name prefix to .ini section.
    IGNORED_PROPERTIES : list[str], class attribute
        Class attribute names that must not be saved.

    Notes
    -----
    Every field is required by the constructor; there are no
    defaults.

    Examples
    --------
    >>> c = Calibration(*[None] * len(Calibration.PROPERTIES))
    >>> c.is_valid()
    False
    >>> c.get_section_for_property("camera_width")
    'camera'
    >>> c.get_proportion_tuple("16:9")
    (16, 9)
    """

    camera_description: str
    camera_id: str
    camera_position: int
    camera_width: int
    camera_height: int
    camera_max_fps: int
    camera_min_fps: int

    screen_manufacturer: str
    screen_model: str
    screen_position: int
    screen_serial_number: str
    screen_width: int
    screen_height: int
    screen_available_width: int
    screen_available_height: int
    screen_pos_x: int
    screen_pos_y: int

    content_width: int
    content_height: int
    content_width_ratio: int
    content_height_ratio: int
    content_proportion: str

    calibration_date: str
    calibration_hour: str

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    ID_VALUE: ClassVar[int] = 1
    PROPORTIONS: ClassVar[dict[str, tuple[int, int]]] = {
        "4:3": (4, 3),
        "16:9": (16, 9),
    }

    SECTIONS_MAP: ClassVar[dict[str, str]] = {
        "camera_": "camera",
        "screen_": "screen",
        "content_": "content",
        "calibration_": "info",
    }

    IGNORED_PROPERTIES: ClassVar[list[str]] = [
        "PROPERTIES",
        "DATA_PROPERTIES",
        "ID_VALUE",
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
