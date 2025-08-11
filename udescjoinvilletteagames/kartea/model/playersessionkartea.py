import dataclasses
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from typing import ClassVar

from udescjoinvilletteagames.kartea.util.pathconfigkartea import \
    PathConfigKartea
from udescjoinvilletteamodel.player import Player


def _get_player_attributes(player_instance):
    """Extrai o nome e o valor do atributo 'player_identifier' de um objeto Player.

    Args:
        player_instance: Instância do objeto Player.

    Returns:
        tuple: Lista com o nome 'player_identifier' e lista com seu valor correspondente.
    """
    if not player_instance:
        return [], []

    if is_dataclass(player_instance):
        identifier_field = next((f for f in fields(player_instance) if f.name == "player_identifier"), None)
        if identifier_field:
            return ["player_identifier"], [getattr(player_instance, "player_identifier")]
        return [], []

    if (
        hasattr(player_instance, "player_identifier")
        and not callable(getattr(player_instance, "player_identifier"))
        and not "player_identifier".startswith("_")
    ):
        return ["player_identifier"], [getattr(player_instance, "player_identifier")]
    return [], []


def _get_field_value(field_obj):
    """Obtém o valor de um campo, tratando default_factory, default e _MISSING_TYPE.

    Args:
        field_obj: Objeto de campo de uma dataclass.

    Returns:
        O valor do campo, considerando default_factory ou default, ou None se ausente.
    """
    from dataclasses import _MISSING_TYPE

    if field_obj.default_factory is not _MISSING_TYPE and callable(field_obj.default_factory):
        return field_obj.default_factory()
    return field_obj.default if field_obj.default is not _MISSING_TYPE else None


def initialize_reflexive(cls):
    """Decorador para inicializar PROPERTIES e DATA_PROPERTIES com base nos campos da classe.

    Exclui o atributo 'player' da lista PROPERTIES e inclui o identifier do player padrão.

    Args:
        cls: Classe a ser decorada.

    Returns:
        Classe com atributos PROPERTIES e DATA_PROPERTIES inicializados.
    """
    cls.PROPERTIES = []
    cls.DATA_PROPERTIES = []

    for field_obj in fields(cls):
        if field_obj.name != "player":
            cls.PROPERTIES.append(field_obj.name)
            cls.DATA_PROPERTIES.append(_get_field_value(field_obj))
        elif field_obj.name == "player" and field_obj.default_factory is not dataclasses._MISSING_TYPE:
            # Adiciona o identifier do player padrão
            player_instance = field_obj.default_factory()
            player_props, player_values = _get_player_attributes(player_instance)
            cls.PROPERTIES.extend(player_props)
            cls.DATA_PROPERTIES.extend(player_values)

    # FILE não é inicializado aqui, será gerenciado por __post_init__
    cls.FILE = None

    return cls


@initialize_reflexive
@dataclass
class PlayerSessionKartea:
    """Modelo sumarizado para os dados da sessão do jogador kartea."""

    # Dados da sessão
    session_identifier: int = 0
    
    # Player
    player: Player = field(default_factory=Player)
    
    # Dados da sessão continuação
    date_session: str = datetime.now().strftime("%d-%m-%Y")
    time_session: str = "00:00:00"  # @TODO: totalizador de tempo de jogo
    start_time: str = datetime.now().strftime("%H:%M:%S")
    start_hour: int = 1

    # Evolução do jogo e pontuação
    phase_reached: int = 1
    level_reached: int = 1
    general_score: int = 0

    # Totalizadores de eventos
    q_movements: int = 0
    q_collided_targets: int = 0
    q_avoided_targets: int = 0
    q_collided_obstacles: int = 0
    q_avoided_obstacles: int = 0

    # Atributos de classe
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    FILE: ClassVar[str | None] = None

    def __post_init__(self):
        """Atualiza FILE, PROPERTIES e DATA_PROPERTIES com base no player e session fornecidos."""
        if self.player:
            # Obtém propriedades e valores do player fornecido
            player_props, player_values = _get_player_attributes(self.player)

            # Atualiza FILE com o session fornecido e identifier do player
            PlayerSessionKartea.FILE = PathConfigKartea.kartea_player(
                f"{self.session_identifier}_{self.player.player_identifier}_kartea_session.csv"
            )

            # Atualiza PROPERTIES e DATA_PROPERTIES
            if "player_identifier" in PlayerSessionKartea.PROPERTIES:
                # Atualiza o valor do identifier
                identifier_index = PlayerSessionKartea.PROPERTIES.index("player_identifier")
                PlayerSessionKartea.DATA_PROPERTIES[identifier_index] = player_values[0]
            else:
                # Adiciona identifier se não estiver presente
                PlayerSessionKartea.PROPERTIES.extend(player_props)
                PlayerSessionKartea.DATA_PROPERTIES.extend(player_values)

            # Atualiza o valor de session em DATA_PROPERTIES
            if "session_identifier" in PlayerSessionKartea.PROPERTIES:
                session_index = PlayerSessionKartea.PROPERTIES.index("session_identifier")
                PlayerSessionKartea.DATA_PROPERTIES[session_index] = self.session_identifier


# Caso com instância fornecida
x = Player(player_identifier=1, name="Player1")
config = PlayerSessionKartea(player=x, session_identifier=42)
print("Com instância fornecida:")
print(PlayerSessionKartea.PROPERTIES)
print(PlayerSessionKartea.DATA_PROPERTIES)
print(PlayerSessionKartea.FILE)

# Caso com valor padrão
config_default = PlayerSessionKartea()
print("\nCom valor padrão:")
print(PlayerSessionKartea.PROPERTIES)
print(PlayerSessionKartea.DATA_PROPERTIES)
print(PlayerSessionKartea.FILE)