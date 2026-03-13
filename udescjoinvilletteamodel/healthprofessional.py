from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar, Dict, List

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from udescjoinvilletteamodel import InstitutionFacility


def initialize_reflexive(cls):
    """
    Initialize class with reflexive properties metadata.

    Populates PROPERTIES with all field names and DATA_PROPERTIES with
    default values of initializable fields.

    Parameters
    ----------
    cls : type
        Class to decorate with reflexive properties.

    Returns
    -------
    type
        The decorated class with PROPERTIES and DATA_PROPERTIES attributes.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class HealthProfessional:
    """
    Health professional entity representing a healthcare professional.
    A HealthProfessional instance encapsulates information about a
    healthcare worker, including their identifier, name, professional type,
    and associated institution or facility.

    Attributes
    ----------
    id : int
        Unique identifier for the health professional.
    name : str
        Full name of the health professional.
    type : int
        Professional type code mapping to TYPE_MAP dictionary.
    institutionfacility : InstitutionFacility
        Reference to the institution or facility where professional works.

    CLASS VARIABLES
    ---------------
    TYPE_MAP : ClassVar[dict[int, str]]
        Mapping of professional type codes to translated type names.
        Used for internationalization via QCoreApplication.
    PROPERTIES : ClassVar[list[str]]
        List of property names for serialization.
    DATA_PROPERTIES : ClassVar[list]
        List of data property definitions.

    Methods
    -------
    is_valid() -> bool
        Validates that all required fields are properly set.
    set_data(data: Dict) -> None
        Sets properties from a dictionary.
    get_data() -> List[Dict]
        Retrieves property data as a list of dictionaries.

    Notes
    -----
    Type codes range from 0-20 representing different healthcare professions
    including nurses, psychologists, physiotherapists, and others.
    """

    id: int
    name: str
    type: int
    institutionfacility: "InstitutionFacility"

    # Mapping prefixes to .ini sections
    TYPE_MAP: ClassVar[dict[int, str]] = {
        0: "",
        1: QCoreApplication.translate("HealthProfessional", "Arteterapeuta"),
        2: QCoreApplication.translate(
            "HealthProfessional", "Assistente Social"
        ),
        3: QCoreApplication.translate(
            "HealthProfessional", "Cuidador Especializado"
        ),
        4: QCoreApplication.translate("HealthProfessional", "Educador Físico"),
        5: QCoreApplication.translate("HealthProfessional", "Enfermeiro"),
        6: QCoreApplication.translate("HealthProfessional", "Fisioterapeuta"),
        7: QCoreApplication.translate("HealthProfessional", "Fonoaudiólogo"),
        8: QCoreApplication.translate("HealthProfessional", "Geneticista"),
        9: QCoreApplication.translate(
            "HealthProfessional", "Mediador Escolar"
        ),
        10: QCoreApplication.translate(
            "HealthProfessional", "Musicoterapeuta"
        ),
        11: QCoreApplication.translate("HealthProfessional", "Neuropediatra"),
        12: QCoreApplication.translate("HealthProfessional", "Neurologista"),
        13: QCoreApplication.translate("HealthProfessional", "Nutricionista"),
        14: QCoreApplication.translate("HealthProfessional", "Pediatra"),
        15: QCoreApplication.translate(
            "HealthProfessional", "Professor Educação Especial"
        ),
        16: QCoreApplication.translate("HealthProfessional", "Psicopedagogo"),
        17: QCoreApplication.translate("HealthProfessional", "Psicólogo"),
        18: QCoreApplication.translate("HealthProfessional", "Psiquiatra"),
        19: QCoreApplication.translate(
            "HealthProfessional", "Terapeuta Ocupacional"
        ),
        20: QCoreApplication.translate("HealthProfessional", "Voluntário"),
    }

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
        """
        Validate the health professional object.

        Checks that id is a valid integer, name is non-empty, type is a valid
        integer mapped in TYPE_MAP, and all non-strong properties are not None.

        Returns
        -------
        bool
            True if the health professional object is valid, False otherwise.

        Examples
        --------
        >>> hp = HealthProfessional(id=1, name="Dr. Smith",
        ...     type=5, institutionfacility=None)
        >>> hp.is_valid()
        True

        >>> hp_invalid = HealthProfessional(id=None, name="",
        ...     type=99, institutionfacility=None)
        >>> hp_invalid.is_valid()
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
        """
        Set object attributes from a dictionary.
        Iterates through defined properties and assigns corresponding
        values from the input dictionary to the object instance.

        Parameters
        ----------
        data : Dict
            Dictionary containing property names as keys and their
            respective values to be assigned to the object.
        """
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        """
        Retrieve health professional data as a list containing a dictionary.

        Extracts all properties except 'institutionfacility', which is
        converted to its ID if present, otherwise None.

        Returns
        -------
        List[Dict]
            A list containing a single dictionary with health professional
            attributes and facility ID.

        Examples
        --------
        >>> hp = HealthProfessional(id=1, name="Dr. Smith",
        ...     type=5, institutionfacility=None)
        >>> data = hp.get_data()
        >>> data[0]['id']
        1
        >>> data[0]['name']
        'Dr. Smith'
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
