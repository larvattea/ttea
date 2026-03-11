from dataclasses import dataclass, fields
from datetime import datetime
from typing import ClassVar, Dict, List

from PySide6.QtCore import QCoreApplication


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
class InstitutionFacility:
    id: int
    name: str
    address: str
    phone: str
    email: str
    website: str
    social_network: str
    type: int

    # Mapping prefixes to .ini sections
    TYPE_MAP: ClassVar[dict[int, str]] = {
        0: "",
        1: QCoreApplication.translate("InstitutionFacility", "Clínica"),
        2: QCoreApplication.translate("InstitutionFacility", "Consultório"),
        3: QCoreApplication.translate("InstitutionFacility", "Hospital"),
        4: QCoreApplication.translate(
            "InstitutionFacility", "Instituição Comunitária"
        ),
        5: QCoreApplication.translate(
            "InstitutionFacility", "Instituição de Ensino"
        ),
        6: QCoreApplication.translate("InstitutionFacility", "Outro"),
        7: QCoreApplication.translate("InstitutionFacility", "Posto de Saúde"),
    }

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
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
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]
