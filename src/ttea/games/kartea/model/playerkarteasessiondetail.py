from dataclasses import dataclass, fields
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Dict, List

# from PyQt6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaSession


def QT_TRANSLATE_NOOP(context: str, text: str) -> str:
    return text


def initialize_reflexive(cls):
    """Decorator to initialize class reflection data statically.

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
    - Adds field names to `PROPERTIES`.
    - Adds default values of initializable fields to `DATA_PROPERTIES`.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class PlayerKarteaSessionDetail:
    """Detailed model for Kartea player session event data."""

    class EventType(str, Enum):
        # Collisions and Deviations
        COLLIDED_TARGET = "Colidiu com Alvo"
        COLLIDED_OBSTACLE = "Colidiu com Obstáculo"
        AVOIDED_TARGET = "Desviou de Alvo"
        AVOIDED_OBSTACLE = "Desviou de Obstáculo"

        # Creation
        CREATED_TARGET = "Criou Alvo"
        CREATED_OBSTACLE = "Criou Obstáculo"

        # Player Movement
        CHANGED_LANE = "Trocou de Pista"
        LEFT_GAME_AREA = "Saiu da área do jogo"

        # Game Control / Level Progression
        GAME_CONTROL_ADVANCE_LEVEL = "Controle Jogo: Avanca Nível"
        GAME_CONTROL_MAINTAIN_LEVEL = "Controle Jogo: Permanece Nível"
        GAME_CONTROL_REGRESS_LEVEL = "Controle Jogo: Retrocede Nível"

        # Control UFE (HUD, Áudio, Pause)
        UFE_CONTROL_ENABLE_HUD = "Controle UFE: Habilita HUD"
        UFE_CONTROL_DISABLE_HUD = "Controle UFE: Desabilita HUD"
        UFE_CONTROL_ENABLE_SOUND = "Controle UFE: Habilita Som"
        UFE_CONTROL_DISABLE_SOUND = "Controle UFE: Desabilita Som"
        UFE_CONTROL_PAUSE = "Controle UFE: Pause"
        UFE_CONTROL_UNPAUSE = "Controle UFE: Unpause"

        @property
        def display_name(self) -> str:
            """Retorna o nome do evento traduzido no idioma ativo do Qt."""
            try:
                from PyQt6.QtCore import QCoreApplication

                return QCoreApplication.translate(
                    "PlayerKarteaSessionDetail", self.value
                )
            except ImportError:
                return self.value

    _TRANSLATIONS: ClassVar[tuple[str, ...]] = (
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Colidiu com Alvo"),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Colidiu com Obstáculo"
        ),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Desviou de Alvo"),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Desviou de Obstáculo"),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Criou Alvo"),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Criou Obstáculo"),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Trocou de Pista"),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Saiu da área do jogo"),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle Jogo: Avanca Nível"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle Jogo: Permanece Nível"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle Jogo: Retrocede Nível"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Habilita HUD"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Desabilita HUD"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Habilita Som"
        ),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Desabilita Som"
        ),
        QT_TRANSLATE_NOOP("PlayerKarteaSessionDetail", "Controle UFE: Pause"),
        QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Unpause"
        ),
    )

    id: int
    session: "PlayerKarteaSession"
    date_time: str
    event_time: str
    phase: int
    level: int
    player_position: int
    event_position: int
    event_type: EventType | str
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def set_data(self, data: Dict) -> None:
        """Update session detail data from a dictionary."""
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        """Return session detail data as a list of dictionaries."""
        info = {
            prop: getattr(self, prop)
            for prop in self.PROPERTIES
            if prop != "session"
        }
        info["session"] = self.session.id if self.session else None
        if isinstance(info.get("event_type"), Enum):
            info["event_type"] = info["event_type"].value
        return [info]
