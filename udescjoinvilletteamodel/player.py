from dataclasses import dataclass, fields
from typing import ClassVar
from datetime import datetime
from udescjoinvilletteautil.pathconfig import PathConfig

# def initialize_reflexive(cls):
#     """Decorador para inicializar dados de reflexão do jogador estaticamente."""
#     cls.PROPERTIES = [field.name for field in fields(cls)]
#     cls.DATA_PROPERTIES = [field.default for field in fields(cls)]
#     cls.FILE = PathConfig.kartea_player(f"{cls.identifier}_{cls.name}_player.csv")
#     return cls

# @initialize_reflexive

@dataclass
class Player:
    """Modelo para os dados do jogador."""
    player_identifier: int = 0 
    name: str = ""
    birth_date: datetime = None
    observations: str = ""

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    FILE: ClassVar[str | None] = None

    def is_valid(self) -> bool:
        """Valida se os dados estão preenchidos corretamente."""
        return bool(self.name and self.birth_date)