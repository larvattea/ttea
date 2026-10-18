"""Model of a player's Kartea game configuration."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .reflexivemodel import ReflexiveModel, initialize_reflexive

# Imported only for type checking, to avoid circular imports at
# runtime.
if TYPE_CHECKING:
    from ttea.games.kartea.model import (
        KarteaPhase,
        KarteaPhaseLevel,
        PlayerKarteaSession,
    )
    from ttea.model import Player


@initialize_reflexive
@dataclass
class PlayerKarteaConfig(ReflexiveModel):
    """Model for player configuration in the Kartea game.

    Attributes
    ----------
    player : Player
        The player associated with this configuration.
    session : PlayerKarteaSession
        Last game session recorded in this configuration.
    update_session_id : bool
        Whether each new game session is written to ``session``
        (UPDATE_SESSION_ID_YES) or the recorded session is kept
        (UPDATE_SESSION_ID_NO).
    phase : KarteaPhase
        The game phase for this configuration.
    level : KarteaPhaseLevel
        The level within the phase for this configuration.
    level_time : int
        Time allocated for the level (in seconds).
    vehicle_image : str
        Vehicle image resource (see KarteaResourceFields).
    environment_image_right : str
        Environment image drawn on the right side of the track.
    environment_image_left : str
        Environment image drawn on the left side of the track.
    target_image : str
        Target image resource.
    obstacle_image : str
        Obstacle image resource.
    positive_feedback_image : str
        Positive feedback image resource.
    neutral_feedback_image : str
        Neutral feedback image resource.
    negative_feedback_image : str
        Negative feedback image resource.
    positive_feedback_sound : str
        Positive feedback sound resource.
    neutral_feedback_sound : str
        Neutral feedback sound resource.
    negative_feedback_sound : str
        Negative feedback sound resource.
    palette : int
        Number of the track color palette (key of KarteaPalettes.ALL);
        unknown numbers fall back to the default palette (0).
    hud : bool
        Whether the heads-up display (HUD) is enabled.
    sound : bool
        Whether sound effects are enabled.
    feedback_image_time : float
        Time (in seconds, 0 to 2, step 0.1) the positive/negative
        feedback image stays on screen. 0 shows it for a single frame
        (original behavior). Defaults to 0.0.
    object_arrival_time_1 : float
        Time (in seconds, 5 to 10, step 0.1) an object takes from
        appearing on the road to reaching the car at speed 1
        (levels 1 and 2). Defaults to 6.5.
    object_arrival_time_2 : float
        Same for speed 2 (levels 3 and 4): 3 to 5 s. Defaults to
        3.3. Must be lower than object_arrival_time_1.
    object_arrival_time_3 : float
        Same for speed 3 (levels 5 to 7): 1 to 3 s. Defaults to
        2.2. Must be lower than object_arrival_time_2.
    feet_marker : bool
        Whether a marker (yellow dot) is drawn at the player's real
        feet position during the game. Defaults to False.
    feet_click : bool
        Whether the player can select menu buttons with the feet,
        standing on a button for ``feet_click_time`` seconds. When
        enabled, the marker is always shown in the menus. Defaults
        to False.
    feet_click_time : float
        Time (in seconds, 0.5 to 3, step 0.1) the player must stay on
        a button to select it with the feet. Defaults to 1.2.
    horizon_image : str
        Horizon image resource, drawn behind the track (see
        KarteaResourceFields). Defaults to "horizon". Comes last so
        that CSV files written before this column existed can still
        be loaded.
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the class, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field (``dataclasses.MISSING`` when
        the field has none), filled by ``initialize_reflexive``.
    REF_PROPERTIES : tuple[str, ...], class attribute
        Fields written as the referenced object's ``id`` by
        ``get_data``: player, session, phase and level.
    UPDATE_SESSION_ID_NO : bool, class attribute
        Value of ``update_session_id`` that keeps the recorded
        session (False).
    UPDATE_SESSION_ID_YES : bool, class attribute
        Value of ``update_session_id`` that records each new session
        (True). Default for new configurations.

    Methods
    -------
    is_valid()
        Check whether the required references are set.
    set_data(data)
        Update configuration data from a dictionary.
    get_data()
        Return configuration data as a list with one dictionary.

    Notes
    -----
    The image and sound fields hold resource names listed by
    KarteaResourceFields (built-in resources or files in the mods
    folder). The fields with defaults come last so that CSV files
    written before those columns existed can still be loaded.

    Examples
    --------
    >>> from types import SimpleNamespace
    >>> config = PlayerKarteaConfig(
    ...     player=SimpleNamespace(id=1),
    ...     session=SimpleNamespace(id=10),
    ...     update_session_id=PlayerKarteaConfig.UPDATE_SESSION_ID_YES,
    ...     phase=SimpleNamespace(id=1),
    ...     level=SimpleNamespace(id=2),
    ...     level_time=60,
    ...     vehicle_image="defaultvehicle",
    ...     environment_image_right="right",
    ...     environment_image_left="left",
    ...     target_image="defaultstar",
    ...     obstacle_image="defaultobstacle",
    ...     positive_feedback_image="positive",
    ...     neutral_feedback_image="neutral",
    ...     negative_feedback_image="negative",
    ...     positive_feedback_sound="point",
    ...     neutral_feedback_sound="miss",
    ...     negative_feedback_sound="miss",
    ...     palette=0,
    ...     hud=True,
    ...     sound=True,
    ... )
    >>> config.is_valid()
    True
    >>> data = config.get_data()[0]
    >>> data["player"], data["session"], data["phase"], data["level"]
    (1, 10, 1, 2)
    >>> data["object_arrival_time_1"]
    6.5
    >>> data["horizon_image"]
    'horizon'
    """

    player: "Player"
    session: "PlayerKarteaSession"
    update_session_id: bool
    phase: "KarteaPhase"
    level: "KarteaPhaseLevel"
    level_time: int
    vehicle_image: str
    environment_image_right: str
    environment_image_left: str
    target_image: str
    obstacle_image: str
    positive_feedback_image: str
    neutral_feedback_image: str
    negative_feedback_image: str
    positive_feedback_sound: str
    neutral_feedback_sound: str
    negative_feedback_sound: str
    palette: int
    hud: bool
    sound: bool
    # Fields with defaults stay last: CSVs written before these columns
    # existed can still be loaded.
    feedback_image_time: float = 0.0
    # Used as GameSettings.OBJECT_ARRIVAL_TIME. Defaults equal to those
    # of KarteaArrivalTimeFields.ALL.
    object_arrival_time_1: float = 6.5
    object_arrival_time_2: float = 3.3
    object_arrival_time_3: float = 2.2
    feet_marker: bool = False
    feet_click: bool = False
    feet_click_time: float = 1.2
    # Default equal to that of KarteaResourceFields.ALL.
    horizon_image: str = "horizon"
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    REF_PROPERTIES = ("player", "session", "phase", "level")
    UPDATE_SESSION_ID_NO = False
    UPDATE_SESSION_ID_YES = True

    def is_valid(self) -> bool:
        """Check whether the required references are set.

        Returns
        -------
        bool
            True if ``player``, ``phase`` and ``level`` are all set
            (truthy), False otherwise.
        """
        return bool(self.player and self.phase and self.level)
