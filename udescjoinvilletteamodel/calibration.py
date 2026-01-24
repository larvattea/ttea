from dataclasses import dataclass, fields
from typing import ClassVar, Dict, List


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
class Calibration:
    camera_position: int
    camera_description: str

    control_height_proportion: int
    control_width_proportion: int

    monitor_manufacturer: str
    monitor_model: str
    monitor_serial_number: str

    monitor_height: int
    monitor_width: int

    proportion: str
    proportion_value: str

    height_ratio: int
    width_ratio: int

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    PROPORTIONS: ClassVar[dict[str, tuple[int, int]]] = {
        "4:3": (4, 3),
        "16:9": (16, 9),
    }

    def is_valid(self) -> bool:
        return (
            self.camera_position
            and self.camera_description
            and self.control_height_proportion
            and self.control_width_proportion
            and self.monitor_manufacturer
            and self.monitor_model
            and self.monitor_serial_number
            and self.monitor_height
            and self.monitor_width
            and self.proportion
            and self.proportion_value
            and self.height_ratio
            and self.width_ratio
        )

    def set_data(self, data: Dict) -> None:
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]
