"""Institution/facility model: places where the platform is used."""

from dataclasses import dataclass, fields
from typing import ClassVar, Dict, List

from PySide6.QtCore import QT_TRANSLATE_NOOP


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
class InstitutionFacility:
    """Health institution / facility entity.

    Represents a service location with contact information.

    Attributes
    ----------
    id : int
        Unique identifier for the facility.
    name : str
        Facility name.
    address : str
        Physical address.
    phone : str
        Contact phone number.
    email : str
        Contact email address.
    website : str
        Website URL.
    social_network : str
        Social network or messaging endpoint.
    type : int
        Facility type code, a key of ``TYPE_MAP``.
    TYPE_MAP : dict[int, str], class attribute
        Facility type codes (0 to 7) to pt_BR type names; 0 is the
        empty "no type" entry.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.

    Methods
    -------
    is_valid() -> bool
        Validate required fields.
    set_data(data: dict) -> None
        Populate fields from a dict.
    get_data() -> list[dict]
        Export fields as a list containing one dict.

    Notes
    -----
    The ``TYPE_MAP`` names are marked with ``QT_TRANSLATE_NOOP`` in
    the ``"InstitutionFacility"`` context: this only registers the
    pt_BR source texts for pyside6-lupdate. They are translated at
    display time with ``QCoreApplication.translate`` in that
    context, so a language change takes effect immediately.
    """

    id: int
    name: str
    address: str
    phone: str
    email: str
    website: str
    social_network: str
    type: int

    TYPE_MAP: ClassVar[dict[int, str]] = {
        0: "",
        1: QT_TRANSLATE_NOOP("InstitutionFacility", "Clínica"),
        2: QT_TRANSLATE_NOOP("InstitutionFacility", "Consultório"),
        3: QT_TRANSLATE_NOOP("InstitutionFacility", "Hospital"),
        4: QT_TRANSLATE_NOOP("InstitutionFacility", "Instituição Comunitária"),
        5: QT_TRANSLATE_NOOP("InstitutionFacility", "Instituição de Ensino"),
        6: QT_TRANSLATE_NOOP("InstitutionFacility", "Outro"),
        7: QT_TRANSLATE_NOOP("InstitutionFacility", "Posto de Saúde"),
    }

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
        """Validate the facility object.

        Returns
        -------
        bool
            True if the object is valid, False otherwise.

        Notes
        -----
        ``id`` must be an int, ``name`` must not be blank and ``type``
        must be an int key of ``TYPE_MAP``; the other fields may be
        empty but not None.

        Examples
        --------
        >>> inst = InstitutionFacility(1, 'A', '', '', '', '', '', 0)
        >>> inst.is_valid()
        True
        >>> inst = InstitutionFacility(None, '', '', '', '', '', '', 0)
        >>> inst.is_valid()
        False
        """
        if self.id is None or not isinstance(self.id, int):
            return False

        if not self.name or not self.name.strip():
            return False

        if not isinstance(self.type, int) or self.type not in self.TYPE_MAP:
            return False

        strong_fields = {"id", "name", "type"}

        for prop in self.PROPERTIES:
            if prop not in strong_fields:
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

        Examples
        --------
        >>> inst = InstitutionFacility(1, 'A', '', '', '', '', '', 0)
        >>> inst.set_data({'name': 'B', 'type': 1})
        >>> inst.name
        'B'
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

        Examples
        --------
        >>> inst = InstitutionFacility(1, 'A', '', '', '', '', '', 0)
        >>> inst.get_data()[0]['name']
        'A'
        """
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]
