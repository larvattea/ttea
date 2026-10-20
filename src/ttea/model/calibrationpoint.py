"""Calibration point model: the four corners of the projection.

Holds the corner points saved in the calibration point CSV file
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
class CalibrationPoint:
    """Four corner points of the calibrated projection area.

    Attributes
    ----------
    pointx1, pointy1 : int
        Coordinates of the first corner.
    pointx2, pointy2 : int
        Coordinates of the second corner.
    pointx3, pointy3 : int
        Coordinates of the third corner.
    pointx4, pointy4 : int
        Coordinates of the fourth corner.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.
    ID_VALUE : int, class attribute
        Fixed identifier of the single calibration point record (1).

    Notes
    -----
    TODO(doc): confirm the corner order and the coordinate space
    (screen or camera pixels).

    Examples
    --------
    >>> p = CalibrationPoint(0, 0, 640, 0, 0, 480, 640, 480)
    >>> p.set_data({"pointx1": 10})
    >>> p.get_data()[0]["pointx1"]
    10
    """

    pointx1: int
    pointy1: int
    pointx2: int
    pointy2: int
    pointx3: int
    pointy3: int
    pointx4: int
    pointy4: int

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    ID_VALUE: ClassVar[int] = 1

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
