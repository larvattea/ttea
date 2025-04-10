from dataclasses import dataclass
from datetime import datetime

@dataclass
class Player:
    """Modelo para os dados do jogador."""
    name: str = ""
    birth_date: datetime = None
    observations: str = ""

    def is_valid(self) -> bool:
        """Valida se os dados estão preenchidos corretamente."""
        return bool(self.name and self.birth_date)