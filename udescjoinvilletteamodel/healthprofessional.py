from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar, Dict, List

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from udescjoinvilletteamodel import InstitutionFacility


def initialize_reflexive(cls):
    """Decorator to statically initialize player reflection data.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with initialized PROPERTIES and DATA_PROPERTIES.

    Notes
    -----
    - Adds the list of field names to `PROPERTIES`.
    - Adds default values of initializable fields to `DATA_PROPERTIES`.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class HealthProfessional:
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
        for prop in self.PROPERTIES:
            value = getattr(self, prop)

            # Generic validation for None
            if value is None:
                return False

        return True

    def set_data(self, data: Dict) -> None:
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        info = {
            prop: getattr(self, prop)
            for prop in self.PROPERTIES
            if prop not in ["institutionfacility"]
        }
        info["institutionfacility"] = (
            self.institutionfacility.id if self.institutionfacility else None
        )
        return [info]
