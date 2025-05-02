from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime
import dataclasses
from typing import ClassVar
from udescjoinvilletteagames.kartea.model.playersessionkartea import PlayerSessionKartea
from udescjoinvilletteagames.kartea.util.pathconfigkartea import PathConfigKartea

def _get_session_attributes(session_instance):
    """Extrai o nome e o valor do atributo 'identifier' de um objeto PlayerSessionKartea.

    Args:
        player_instance: Instância do objeto Player.

    Returns:
        tuple: Lista com o nome 'identifier' e lista com seu valor correspondente.
    """
    if not session_instance:
        return [], []

    if is_dataclass(session_instance):
        identifier_field = next((f for f in fields(session_instance) if f.name == "session"), None)
        if identifier_field:
            return ["identifier"], [getattr(session_instance, "identifier")]
        return [], []

    # Para objetos não-dataclass
    if (
        hasattr(session_instance, "identifier")
        and not callable(getattr(session_instance, "identifier"))
        and not "identifier".startswith("_")
    ):
        return ["identifier"], [getattr(session_instance, "identifier")]
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
        if field_obj.name != "session":
            cls.PROPERTIES.append(field_obj.name)
            cls.DATA_PROPERTIES.append(_get_field_value(field_obj))
        elif field_obj.name == "session":
            # Inicializa com a sessão padrão (default_factory) se disponível
            if field_obj.default_factory is not dataclasses._MISSING_TYPE:
                session_instance = field_obj.default_factory()
                player_props, player_values = _get_session_attributes(session_instance)
                cls.PROPERTIES.extend(player_props)  # Adiciona 'identifier'
                cls.DATA_PROPERTIES.extend(player_values)  # Adiciona valor do identifier
                # Inicializa FILE com o player padrão
                cls.FILE = PathConfigKartea.kartea_player(
                    f"{session_instance.identifier}_kartea_session_detail.csv"
                )

    return cls


@initialize_reflexive
@dataclass
class PlayerSessionDetailKartea:
    """Modelo detalhado os dados da sessao do jogador kartea."""
    
    # Sesssão do jogador
    session: PlayerSessionKartea = field(default_factory=PlayerSessionKartea)

    # Dados da sessão detalhados
    identifier: int = 0
    event_time: str = "00:00:00" #@TODO: totalizador de tempo de jogo
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
        if self.session:
            # Obtém propriedades e valores da sessão fornecida
            session_props, session_values = _get_session_attributes(self.session)
            
            # Atualiza FILE com base na sessão fornecida
            PlayerSessionDetailKartea.FILE = PathConfigKartea.kartea_player(
                f"{self.session.identifier}_kartea_session_detail.csv"
            )
            
            # Atualiza PROPERTIES e DATA_PROPERTIES apenas para o identifier
            if "identifier" in PlayerSessionDetailKartea.PROPERTIES:
                # Remove o identifier antigo de DATA_PROPERTIES
                identifier_index = PlayerSessionDetailKartea.PROPERTIES.index("identifier")
                if identifier_index < len(PlayerSessionDetailKartea.DATA_PROPERTIES):
                    PlayerSessionDetailKartea.DATA_PROPERTIES[identifier_index] = session_values[0]
            else:
                # Adiciona identifier se não estiver presente
                PlayerSessionDetailKartea.PROPERTIES.extend(session_props)
                PlayerSessionDetailKartea.DATA_PROPERTIES.extend(session_values)

