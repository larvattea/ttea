from dataclasses import dataclass, field, fields, is_dataclass
import dataclasses
from typing import ClassVar
from udescjoinvilletteamodel.player import Player
from udescjoinvilletteagames.kartea.util.pathconfigkartea import PathConfigKartea


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

    # Para objetos não-dataclass
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
    """Decorador para inicializar PROPERTIES e DATA_PROPERTIES com base no player.

    Exclui o atributo 'player' da lista PROPERTIES e inclui o identifier do player.

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
        elif field_obj.name == "player":
            # Inicializa com o player padrão (default_factory) se disponível
            if field_obj.default_factory is not dataclasses._MISSING_TYPE:
                player_instance = field_obj.default_factory()
                player_props, player_values = _get_player_attributes(player_instance)
                cls.PROPERTIES.extend(player_props)  # Adiciona 'identifier'
                cls.DATA_PROPERTIES.extend(player_values)  # Adiciona valor do identifier
                # Inicializa FILE com o player padrão
                cls.FILE = PathConfigKartea.kartea_player(
                    f"{player_instance.player_identifier}_kartea_config.csv"
                )

    return cls


@initialize_reflexive
@dataclass
class PlayerConfigKartea:
    """Modelo para configuração do jogador no jogo Kartea."""

    # Player
    player: Player = field(default_factory=Player)

    # Configurações do jogo
    current_phase: int = 1
    current_level: int = 1
    session: int = 1
    level_time: int = 120

    # Recursos visuais
    car: str = PathConfigKartea.kartea_image("carro.png")
    environment: str = PathConfigKartea.kartea_image("ambiente.png")
    target: str = PathConfigKartea.kartea_image("alvo.png")
    obstacle: str = PathConfigKartea.kartea_image("obstaculo.png")

    # Feedback visual
    positive_feedback_image: str = PathConfigKartea.kartea_image("feliz.png")
    neutral_feedback_image: str = PathConfigKartea.kartea_image("neutro.png")
    negative_feedback_image: str = PathConfigKartea.kartea_image("triste.png")

    # Feedback sonoro
    positive_feedback_sound: str = PathConfigKartea.kartea_sound("win.wav")
    neutral_feedback_sound: str = PathConfigKartea.kartea_sound("miss.wav")
    negative_feedback_sound: str = PathConfigKartea.kartea_sound("crash.wav")

    # Configurações de interface
    palette: int = 0
    hud: bool = True
    sound: bool = True

    # Atributos de classe
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    FILE: ClassVar[str | None] = None

    def __post_init__(self):
        """Atualiza FILE, PROPERTIES e DATA_PROPERTIES com base no player fornecido."""
        if self.player:
            # Obtém propriedades e valores do player fornecido
            player_props, player_values = _get_player_attributes(self.player)
            
            # Atualiza FILE com base no player fornecido
            PlayerConfigKartea.FILE = PathConfigKartea.kartea_player(
                f"{self.player.player_identifier}_kartea_config.csv"
            )
            
            # Atualiza PROPERTIES e DATA_PROPERTIES apenas para o player_identifier
            if "player_identifier" in PlayerConfigKartea.PROPERTIES:
                # Remove o player_identifier antigo de DATA_PROPERTIES
                identifier_index = PlayerConfigKartea.PROPERTIES.index("player_identifier")
                if identifier_index < len(PlayerConfigKartea.DATA_PROPERTIES):
                    PlayerConfigKartea.DATA_PROPERTIES[identifier_index] = player_values[0]
            else:
                # Adiciona identifier se não estiver presente
                PlayerConfigKartea.PROPERTIES.extend(player_props)
                PlayerConfigKartea.DATA_PROPERTIES.extend(player_values)


# Exemplo de uso
# Caso com instância fornecida
x = Player(player_identifier=1, name="Player1")
config = PlayerConfigKartea(player=x)
print("Com instância fornecida:")
print(PlayerConfigKartea.PROPERTIES)
print(PlayerConfigKartea.DATA_PROPERTIES)
print(PlayerConfigKartea.FILE)

# Caso com valor padrão
config_default = PlayerConfigKartea()
print("\nCom valor padrão:")
print(PlayerConfigKartea.PROPERTIES)
print(PlayerConfigKartea.DATA_PROPERTIES)
print(PlayerConfigKartea.FILE)