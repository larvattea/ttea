"""Model of a player's Kartea game session."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .reflexivemodel import ReflexiveModel, initialize_reflexive

# Imported only for type checking, to avoid circular imports at
# runtime.
if TYPE_CHECKING:
    from ttea.model import Player, Professional


@initialize_reflexive
@dataclass
class PlayerKarteaSession(ReflexiveModel):
    """Summary model for Kartea player session data.

    Attributes
    ----------
    id : int
        Unique identifier for the session.
    player : Player
        The player associated with this session.
    professional : Professional
        The professional who conducted the session.
    start_date : str
        Session start date, ISO 8601 "%Y-%m-%d" (e.g. "2026-09-11").
    start_time : str
        Session start time, ISO 8601 "%H:%M:%S" (local time).
    end_date : str
        Session end date (last save), ISO 8601 "%Y-%m-%d".
    end_time : str
        Session end time (last save), ISO 8601 "%H:%M:%S" (local
        time).
    phase_reached : int
        Current (last) phase of the session; follows the game,
        including when the professional regresses. Same as the
        player's config and the last event in the session detail.
    level_reached : int
        Current (last) level of the session (same rule as
        phase_reached).
    general_score : int
        Overall score achieved in the session.
    q_movement : int
        Number of movement events.
    q_collided_target : int
        Number of target collisions.
    q_avoided_target : int
        Number of avoided targets.
    q_collided_obstacle : int
        Number of obstacle collisions.
    q_avoided_obstacle : int
        Number of avoided obstacles.
    utc_offset : str
        UTC offset of the local dates/times above, ISO 8601 "+HH:MM"
        (e.g. "-03:00"), taken at the start of the session. Defaults
        to "" (sessions recorded before this column existed).
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the class, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field (``dataclasses.MISSING`` when
        the field has none), filled by ``initialize_reflexive``.
    REF_PROPERTIES : tuple[str, ...], class attribute
        Fields written as the referenced object's ``id`` by
        ``get_data``: ``("player", "professional")``.

    Methods
    -------
    set_data(data)
        Update session data from a dictionary.
    get_data()
        Return session data as a list with one dictionary.

    Notes
    -----
    ``utc_offset`` has a default and comes last so that CSV files
    written before this column existed can still be loaded.

    Examples
    --------
    >>> from types import SimpleNamespace
    >>> session = PlayerKarteaSession(
    ...     id=1,
    ...     player=SimpleNamespace(id=1),
    ...     professional=SimpleNamespace(id=2),
    ...     start_date="2025-09-17",
    ...     start_time="10:00:00",
    ...     end_date="2025-09-17",
    ...     end_time="10:30:00",
    ...     phase_reached=2,
    ...     level_reached=3,
    ...     general_score=100,
    ...     q_movement=50,
    ...     q_collided_target=10,
    ...     q_avoided_target=20,
    ...     q_collided_obstacle=5,
    ...     q_avoided_obstacle=15,
    ...     utc_offset="-03:00",
    ... )
    >>> data = session.get_data()[0]
    >>> data["player"], data["professional"]
    (1, 2)
    >>> data["utc_offset"]
    '-03:00'
    """

    id: int
    player: "Player"
    professional: "Professional"
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    phase_reached: int
    level_reached: int
    general_score: int
    q_movement: int
    q_collided_target: int
    q_avoided_target: int
    q_collided_obstacle: int
    q_avoided_obstacle: int
    # Default value and last position: CSVs written before this column
    # existed can still be loaded.
    utc_offset: str = ""
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    REF_PROPERTIES = ("player", "professional")
