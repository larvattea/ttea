import dataclasses
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
from typing import ClassVar

from udescjoinvilletteagames.kartea.model.playersessionkartea import \
    PlayerSessionKartea
from udescjoinvilletteagames.kartea.util.pathconfigkartea import \
    PathConfigKartea
from udescjoinvilletteamodel.player import Player


def _get_session_attributes(session_instance):
    """Extrai o nome e o valor do atributo 'session_identifier' de um objeto PlayerSessionKartea.

    Args:
        session_instance: Instância do objeto PlayerSessionKartea.

    Returns:
        tuple: Lista com o nome 'session_identifier' e lista com seu valor correspondente.
    """
    if not session_instance:
        return [], []

    if is_dataclass(session_instance):
        identifier_field = next((f for f in fields(session_instance) if f.name == "session_identifier"), None)
        if identifier_field:
            return ["session_identifier"], [getattr(session_instance, "session_identifier")]
        return [], []

    if (
        hasattr(session_instance, "session_identifier")
        and not callable(getattr(session_instance, "session_identifier"))
        and not "session_identifier".startswith("_")
    ):
        return ["session_identifier"], [getattr(session_instance, "session_identifier")]
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
    """Decorador para inicializar PROPERTIES e DATA_PROPERTIES com base no session.

    Exclui o atributo 'session' da lista PROPERTIES e inclui o session_identifier.

    Args:
        cls: Classe a ser decorada.

    Returns:
        Classe com atributos PROPERTIES e DATA_PROPERTIES inicializados.
    """
    cls.PROPERTIES = []
    cls.DATA_PROPERTIES = []

    for field_obj in fields(cls):
        if field_obj.name != "session":
            cls.PROPERTIES.append(field_obj.name)
            cls.DATA_PROPERTIES.append(_get_field_value(field_obj))
        elif field_obj.name == "session" and field_obj.default_factory is not dataclasses._MISSING_TYPE:
            session_instance = field_obj.default_factory()
            session_props, session_values = _get_session_attributes(session_instance)
            cls.PROPERTIES.extend(session_props)
            cls.DATA_PROPERTIES.extend(session_values)
            cls.FILE = PathConfigKartea.kartea_player(
                f"{session_instance.session_identifier}_kartea_session_detail.csv"
            )

    return cls


@initialize_reflexive
@dataclass
class PlayerSessionDetailKartea:
    """Modelo detalhado dos dados da sessão do jogador Kartea."""
    
    # Sessão do jogador
    session: PlayerSessionKartea = field(default_factory=PlayerSessionKartea)

    # Dados da sessão detalhados
    detail_identifier: int = 0
    event_time: str = "00:00:00"  # @TODO: totalizador de tempo de jogo
    phase: int = 1
    level: int = 1
    player_position: str = "0,0"
    event_position: str = "0,0"
    event_type: str = "none"
    
    # Atributos de classe
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    FILE: ClassVar[str | None] = None
        
    def __post_init__(self):
        """Atualiza FILE, PROPERTIES e DATA_PROPERTIES com base na sessão fornecida."""
        # Inicializa PROPERTIES e DATA_PROPERTIES se necessário
        if not PlayerSessionDetailKartea.PROPERTIES:
            PlayerSessionDetailKartea.PROPERTIES = [f.name for f in fields(self) if f.name != "session"]
            PlayerSessionDetailKartea.DATA_PROPERTIES = [
                getattr(self, f.name) for f in fields(self) if f.name != "session"
            ]

        if self.session:
            # Obtém propriedades e valores da sessão fornecida
            session_props, session_values = _get_session_attributes(self.session)
            
            # Atualiza FILE com base na sessão fornecida
            PlayerSessionDetailKartea.FILE = PathConfigKartea.kartea_player(
                f"{self.session.session_identifier}_kartea_session_detail.csv"
            )
            
            # Atualiza PROPERTIES e DATA_PROPERTIES com session_identifier
            if session_props and session_props[0] not in PlayerSessionDetailKartea.PROPERTIES:
                PlayerSessionDetailKartea.PROPERTIES.append(session_props[0])
                PlayerSessionDetailKartea.DATA_PROPERTIES.append(session_values[0] if session_values else None)
            elif session_props:
                identifier_index = PlayerSessionDetailKartea.PROPERTIES.index(session_props[0])
                if session_values and identifier_index < len(PlayerSessionDetailKartea.DATA_PROPERTIES):
                    PlayerSessionDetailKartea.DATA_PROPERTIES[identifier_index] = session_values[0]

            # Atualiza detail_identifier em DATA_PROPERTIES
            detail_index = PlayerSessionDetailKartea.PROPERTIES.index("detail_identifier")
            PlayerSessionDetailKartea.DATA_PROPERTIES[detail_index] = self.detail_identifier


# Caso com instância fornecida
y = Player(player_identifier=1, name="Player1")
x = PlayerSessionKartea(player=y, session_identifier=30)
config = PlayerSessionDetailKartea(session=x, detail_identifier=1)
print("Com instância fornecida:")
print(PlayerSessionDetailKartea.PROPERTIES)
print(PlayerSessionDetailKartea.DATA_PROPERTIES)
print(PlayerSessionDetailKartea.FILE)

# Caso com valor padrão
config_default = PlayerSessionDetailKartea()
print("\nCom valor padrão:")
print(PlayerSessionDetailKartea.PROPERTIES)
print(PlayerSessionDetailKartea.DATA_PROPERTIES)
print(PlayerSessionDetailKartea.FILE)