"""Data model for professionals linked to an institution facility."""

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar, Dict, List

from PySide6.QtCore import QT_TRANSLATE_NOOP

if TYPE_CHECKING:
    from ttea.model import InstitutionFacility


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
class Professional:
    """Represent a professional linked to an institution or facility.

    Attributes
    ----------
    id : int
        Unique identifier for the professional.
    name : str
        Full name of the professional.
    type : int
        Professional type code, a key of ``TYPE_MAP``.
    institutionfacility : InstitutionFacility
        Institution or facility where the professional works. It may
        be None in an incomplete association, but then ``is_valid``
        returns False.
    TYPE_MAP : dict[int, str], class attribute
        Professional type codes (0 to 20) to pt_BR profession names;
        0 is the empty "no type" entry.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.

    Notes
    -----
    The ``TYPE_MAP`` names are marked with ``QT_TRANSLATE_NOOP`` in
    the ``"Professional"`` context: this only registers the pt_BR
    source texts for pyside6-lupdate. They are translated at display
    time with ``QCoreApplication.translate`` in that context, so a
    language change takes effect immediately.

    Serialization (``get_data``) stores the associated facility by
    its identifier.
    """

    id: int
    name: str
    type: int
    institutionfacility: "InstitutionFacility"

    TYPE_MAP: ClassVar[dict[int, str]] = {
        0: "",
        1: QT_TRANSLATE_NOOP("Professional", "Arteterapeuta"),
        2: QT_TRANSLATE_NOOP("Professional", "Assistente Social"),
        3: QT_TRANSLATE_NOOP("Professional", "Cuidador Especializado"),
        4: QT_TRANSLATE_NOOP("Professional", "Educador Físico"),
        5: QT_TRANSLATE_NOOP("Professional", "Enfermeiro"),
        6: QT_TRANSLATE_NOOP("Professional", "Fisioterapeuta"),
        7: QT_TRANSLATE_NOOP("Professional", "Fonoaudiólogo"),
        8: QT_TRANSLATE_NOOP("Professional", "Geneticista"),
        9: QT_TRANSLATE_NOOP("Professional", "Mediador Escolar"),
        10: QT_TRANSLATE_NOOP("Professional", "Musicoterapeuta"),
        11: QT_TRANSLATE_NOOP("Professional", "Neuropediatra"),
        12: QT_TRANSLATE_NOOP("Professional", "Neurologista"),
        13: QT_TRANSLATE_NOOP("Professional", "Nutricionista"),
        14: QT_TRANSLATE_NOOP("Professional", "Pediatra"),
        15: QT_TRANSLATE_NOOP(
            "Professional", "Professor de Educação Especial"
        ),
        16: QT_TRANSLATE_NOOP("Professional", "Psicopedagogo"),
        17: QT_TRANSLATE_NOOP("Professional", "Psicólogo"),
        18: QT_TRANSLATE_NOOP("Professional", "Psiquiatra"),
        19: QT_TRANSLATE_NOOP("Professional", "Terapeuta Ocupacional"),
        20: QT_TRANSLATE_NOOP("Professional", "Voluntário"),
    }

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
        """Validate the professional object.

        Returns
        -------
        bool
            True if the professional object is valid, False otherwise.

        Notes
        -----
        ``id`` must be an int, ``name`` must not be blank and ``type``
        must be an int key of ``TYPE_MAP``. ``institutionfacility``
        must not be None.

        Examples
        --------
        >>> from types import SimpleNamespace
        >>> facility = SimpleNamespace(id=3)
        >>> hp = Professional(1, "Dr. Smith", 5, facility)
        >>> hp.is_valid()
        True
        >>> Professional(1, "Dr. Smith", 5, None).is_valid()
        False
        >>> Professional(None, "", 99, facility).is_valid()
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
        """
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        """Return the professional data as a one-item list.

        Returns
        -------
        list[dict]
            A list with one dictionary of the field values, where
            ``institutionfacility`` is replaced by the facility ``id``
            (None when there is no facility).

        Examples
        --------
        >>> from types import SimpleNamespace
        >>> hp = Professional(1, "Dr. Smith", 5, SimpleNamespace(id=3))
        >>> hp.get_data()[0]["institutionfacility"]
        3
        >>> Professional(1, "A", 5, None).get_data()[0]["name"]
        'A'
        """
        info = {
            prop: getattr(self, prop)
            for prop in self.PROPERTIES
            if prop not in ["institutionfacility"]
        }
        info["institutionfacility"] = (
            self.institutionfacility.id if self.institutionfacility else None
        )
        return [info]
