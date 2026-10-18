"""Model of an event recorded during a Kartea game session."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

from .reflexivemodel import ReflexiveModel, initialize_reflexive

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaSession


@initialize_reflexive
@dataclass
class PlayerKarteaSessionDetail(ReflexiveModel):
    """Detailed model for Kartea player session event data.

    Each instance is one event (collision, lane change, menu choice,
    ...) written as a row of the player's session detail CSV.

    Attributes
    ----------
    id : int
        Unique identifier for the event.
    session : PlayerKarteaSession
        The session in which the event happened.
    event_date : str
        Event date, ISO 8601 "%Y-%m-%d" (formerly the ``date_time``
        column).
    event_time : str
        Event time, ISO 8601 "%H:%M:%S" (local time).
    phase : int
        Game phase when the event happened.
    level : int
        Game level when the event happened.
    player_position : int
        Lane of the player when the event happened.
    event_position : int
        Lane related to the event: the object's lane for
        collisions/avoidances, the previous lane for lane changes;
        0 when the event has no position.
    event_type : EventType | str
        Type of the event. Holds an ``EventType`` when recorded by the
        game and the plain pt_BR text when read from the CSV.
    EventType : type[Enum], class attribute
        Enumeration of the event types (nested class).
    _DISPLAY_TEXTS : ClassVar[dict[EventType, str]], class attribute
        pt_BR display text of each ``EventType``, marked for
        translation; equal to the value stored in the CSV.
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the class, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field (``dataclasses.MISSING`` when
        the field has none), filled by ``initialize_reflexive``.
    REF_PROPERTIES : tuple[str, ...], class attribute
        Fields written as the referenced object's ``id`` by
        ``get_data``: ``("session",)``.

    Notes
    -----
    Internationalization (i18n): the ``EventType`` values are what the
    CSV stores. The text shown to the user comes from
    ``_DISPLAY_TEXTS``, whose entries are marked with
    ``QT_TRANSLATE_NOOP`` in the ``"PlayerKarteaSessionDetail"``
    context so that pyside6-lupdate extracts them (it only extracts
    string literals, so the texts are repeated there); the translation
    happens at display time through ``EventType.display_name``
    (``QCoreApplication.translate``). Each display text is kept equal
    to its ``EventType`` value. Add an entry to ``_DISPLAY_TEXTS``
    with the same text for every new event.

    Changing a value changes what new rows store: rows already in the
    CSV keep the old text and are read back as plain text. E.g.
    "Controle Jogo: Avanca Nível" and "Controle Jogador: Jogar" are
    now "Controle do Jogo: Avança Nível" and "Controle do Jogador:
    Jogar".

    Examples
    --------
    >>> from types import SimpleNamespace
    >>> EventType = PlayerKarteaSessionDetail.EventType
    >>> detail = PlayerKarteaSessionDetail(
    ...     id=1,
    ...     session=SimpleNamespace(id=5),
    ...     event_date="2025-09-17",
    ...     event_time="10:00:00",
    ...     phase=1,
    ...     level=2,
    ...     player_position=2,
    ...     event_position=1,
    ...     event_type=EventType.CHANGED_LANE,
    ... )
    >>> data = detail.get_data()[0]
    >>> data["session"], data["event_type"]
    (5, 'Trocou de Pista')
    """

    class EventType(str, Enum):
        """Types of events recorded in a session detail.

        Groups of members:

        - ``COLLIDED_*``/``AVOIDED_*``: collisions with and avoidances
          of targets and obstacles.
        - ``CREATED_*``: objects created on the track.
        - ``CHANGED_LANE``, ``LEFT_GAME_AREA``: player movement.
        - ``GAME_CONTROL_*``: level progression decided by the game.
        - ``UFE_CONTROL_*``: HUD, sound, pause, feet marker and feet
          click toggles, and the professional's choices in the pause
          and end-of-level menus (mouse or keyboard).
        - ``PLAYER_CONTROL_*``: the same menu choices made by the
          player with the feet (feet click).

        Notes
        -----
        The enum mixes in ``str``, so each value is the pt_BR text
        written to the CSV; keep the matching entry of
        ``_DISPLAY_TEXTS`` with the same text. Use ``display_name`` to
        show the event in the active Qt language.
        """

        # Collisions and avoidances
        COLLIDED_TARGET = "Colidiu com Alvo"
        COLLIDED_OBSTACLE = "Colidiu com Obstáculo"
        AVOIDED_TARGET = "Desviou de Alvo"
        AVOIDED_OBSTACLE = "Desviou de Obstáculo"

        # Creation
        CREATED_TARGET = "Criou Alvo"
        CREATED_OBSTACLE = "Criou Obstáculo"

        # Player movement
        CHANGED_LANE = "Trocou de Pista"
        LEFT_GAME_AREA = "Saiu da área do jogo"

        # Game control / level progression
        GAME_CONTROL_ADVANCE_LEVEL = "Controle do Jogo: Avança Nível"
        GAME_CONTROL_MAINTAIN_LEVEL = "Controle do Jogo: Permanece Nível"
        GAME_CONTROL_REGRESS_LEVEL = "Controle do Jogo: Retrocede Nível"

        # UFE control (HUD, audio, pause)
        UFE_CONTROL_ENABLE_HUD = "Controle UFE: Habilita HUD"
        UFE_CONTROL_DISABLE_HUD = "Controle UFE: Desabilita HUD"
        UFE_CONTROL_ENABLE_SOUND = "Controle UFE: Habilita Som"
        UFE_CONTROL_DISABLE_SOUND = "Controle UFE: Desabilita Som"
        UFE_CONTROL_PAUSE = "Controle UFE: Pause"
        UFE_CONTROL_UNPAUSE = "Controle UFE: Unpause"
        # Professional's choices in the pause and end-of-level menus
        UFE_CONTROL_ADVANCE_LEVEL = "Controle UFE: Avança Nível"
        UFE_CONTROL_RESTART_LEVEL = "Controle UFE: Reinicia Nível"
        UFE_CONTROL_REGRESS_LEVEL = "Controle UFE: Retrocede Nível"
        UFE_CONTROL_EXIT_GAME = "Controle UFE: Sai do Jogo"
        # Feet marker and feet click (in-game shortcuts)
        UFE_CONTROL_ENABLE_FEET_MARKER = (
            "Controle UFE: Habilita Marcador dos Pés"
        )
        UFE_CONTROL_DISABLE_FEET_MARKER = (
            "Controle UFE: Desabilita Marcador dos Pés"
        )
        UFE_CONTROL_ENABLE_FEET_CLICK = (
            "Controle UFE: Habilita Clique com os Pés"
        )
        UFE_CONTROL_DISABLE_FEET_CLICK = (
            "Controle UFE: Desabilita Clique com os Pés"
        )

        # Choices made by the player in the menus with the feet (feet
        # click). The same choices made with mouse or keyboard are
        # still recorded as "Controle UFE".
        PLAYER_CONTROL_PLAY = "Controle do Jogador: Jogar"
        PLAYER_CONTROL_CONTINUE = "Controle do Jogador: Continuar"
        PLAYER_CONTROL_ADVANCE_LEVEL = "Controle do Jogador: Avança Nível"
        PLAYER_CONTROL_RESTART_LEVEL = "Controle do Jogador: Reinicia Nível"
        PLAYER_CONTROL_REGRESS_LEVEL = "Controle do Jogador: Retrocede Nível"
        PLAYER_CONTROL_EXIT_GAME = "Controle do Jogador: Sai do Jogo"

        @property
        def display_name(self) -> str:
            """Event name translated into the active Qt language.

            Notes
            -----
            Looks up the pt_BR display text in
            ``PlayerKarteaSessionDetail._DISPLAY_TEXTS`` (falling back
            to the stored value) and translates it at runtime with
            ``QCoreApplication.translate`` in the
            ``"PlayerKarteaSessionDetail"`` context (i18n); Qt returns
            the pt_BR text when there is no translation.
            """
            source = PlayerKarteaSessionDetail._DISPLAY_TEXTS.get(
                self, self.value
            )
            return QCoreApplication.translate(
                "PlayerKarteaSessionDetail", source
            )

    _DISPLAY_TEXTS: ClassVar[dict[EventType, str]] = {
        EventType.COLLIDED_TARGET: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Colidiu com Alvo"
        ),
        EventType.COLLIDED_OBSTACLE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Colidiu com Obstáculo"
        ),
        EventType.AVOIDED_TARGET: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Desviou de Alvo"
        ),
        EventType.AVOIDED_OBSTACLE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Desviou de Obstáculo"
        ),
        EventType.CREATED_TARGET: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Criou Alvo"
        ),
        EventType.CREATED_OBSTACLE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Criou Obstáculo"
        ),
        EventType.CHANGED_LANE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Trocou de Pista"
        ),
        EventType.LEFT_GAME_AREA: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Saiu da área do jogo"
        ),
        EventType.GAME_CONTROL_ADVANCE_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogo: Avança Nível"
        ),
        EventType.GAME_CONTROL_MAINTAIN_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogo: Permanece Nível"
        ),
        EventType.GAME_CONTROL_REGRESS_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogo: Retrocede Nível"
        ),
        EventType.UFE_CONTROL_ENABLE_HUD: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Habilita HUD"
        ),
        EventType.UFE_CONTROL_DISABLE_HUD: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Desabilita HUD"
        ),
        EventType.UFE_CONTROL_ENABLE_SOUND: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Habilita Som"
        ),
        EventType.UFE_CONTROL_DISABLE_SOUND: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Desabilita Som"
        ),
        EventType.UFE_CONTROL_PAUSE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Pause"
        ),
        EventType.UFE_CONTROL_UNPAUSE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Unpause"
        ),
        EventType.UFE_CONTROL_ADVANCE_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Avança Nível"
        ),
        EventType.UFE_CONTROL_RESTART_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Reinicia Nível"
        ),
        EventType.UFE_CONTROL_REGRESS_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Retrocede Nível"
        ),
        EventType.UFE_CONTROL_EXIT_GAME: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle UFE: Sai do Jogo"
        ),
        EventType.UFE_CONTROL_ENABLE_FEET_MARKER: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail",
            "Controle UFE: Habilita Marcador dos Pés",
        ),
        EventType.UFE_CONTROL_DISABLE_FEET_MARKER: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail",
            "Controle UFE: Desabilita Marcador dos Pés",
        ),
        EventType.UFE_CONTROL_ENABLE_FEET_CLICK: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail",
            "Controle UFE: Habilita Clique com os Pés",
        ),
        EventType.UFE_CONTROL_DISABLE_FEET_CLICK: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail",
            "Controle UFE: Desabilita Clique com os Pés",
        ),
        EventType.PLAYER_CONTROL_PLAY: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Jogar"
        ),
        EventType.PLAYER_CONTROL_CONTINUE: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Continuar"
        ),
        EventType.PLAYER_CONTROL_ADVANCE_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Avança Nível"
        ),
        EventType.PLAYER_CONTROL_RESTART_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Reinicia Nível"
        ),
        EventType.PLAYER_CONTROL_REGRESS_LEVEL: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Retrocede Nível"
        ),
        EventType.PLAYER_CONTROL_EXIT_GAME: QT_TRANSLATE_NOOP(
            "PlayerKarteaSessionDetail", "Controle do Jogador: Sai do Jogo"
        ),
    }

    id: int
    session: "PlayerKarteaSession"
    event_date: str
    event_time: str
    phase: int
    level: int
    player_position: int
    event_position: int
    event_type: EventType | str
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    REF_PROPERTIES = ("session",)
