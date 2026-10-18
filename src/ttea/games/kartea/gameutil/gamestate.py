"""State of a KarTEA match.

``GameSettings`` holds only the configuration (screen, sizes,
resources), defined once at startup. Everything that changes during
the match (phase/level, score, counters, player lane, current menu,
clock) lives here, in an instance created by ``main`` and handed to
``GameController`` and ``Menu``; there is no global state.
"""

from dataclasses import dataclass, field


@dataclass
class LevelStats:
    """Counters of the level in progress (reset at each new level).

    They are the values shown on the feedback screen.

    Attributes
    ----------
    score : int
        Score of the level. Defaults to 0.
    movement : int
        Lane changes. Defaults to 0.
    targets : int
        Targets created. Defaults to 0.
    targets_collided : int
        Targets hit. Defaults to 0.
    targets_avoided : int
        Targets missed. Defaults to 0.
    obstacles : int
        Obstacles created. Defaults to 0.
    obstacles_collided : int
        Obstacles hit. Defaults to 0.
    obstacles_avoided : int
        Obstacles avoided. Defaults to 0.

    Examples
    --------
    >>> stats = LevelStats(score=5)
    >>> stats.reset()
    >>> stats.score
    0
    """

    score: int = 0
    movement: int = 0
    targets: int = 0
    targets_collided: int = 0
    targets_avoided: int = 0
    obstacles: int = 0
    obstacles_collided: int = 0
    obstacles_avoided: int = 0

    def reset(self) -> None:
        """Reset all level counters to zero."""
        self.__init__()


@dataclass
class SessionStats:
    """Session totals (the whole game run), never reset.

    ``score_done`` and ``movement_done`` accumulate the levels already
    closed; the session total is this accumulated value plus the value
    of the level in progress.

    Attributes
    ----------
    score_done : int
        Score of the closed levels. Defaults to 0.
    movement_done : int
        Lane changes of the closed levels. Defaults to 0.
    collided_target : int
        Targets hit in the session. Defaults to 0.
    avoided_target : int
        Targets missed in the session. Defaults to 0.
    collided_obstacle : int
        Obstacles hit in the session. Defaults to 0.
    avoided_obstacle : int
        Obstacles avoided in the session. Defaults to 0.
    """

    score_done: int = 0
    movement_done: int = 0
    collided_target: int = 0
    avoided_target: int = 0
    collided_obstacle: int = 0
    avoided_obstacle: int = 0

    def close_level(self, level: LevelStats) -> None:
        """Add the level score and lane changes to the accumulated ones.

        Parameters
        ----------
        level : LevelStats
            Counters of the level being closed.
        """
        self.score_done += level.score
        self.movement_done += level.movement

    def totals(self, level: LevelStats) -> dict:
        """Return the session totals in the session row format (DAO).

        Parameters
        ----------
        level : LevelStats
            Counters of the level in progress, added to the accumulated
            score and movement.

        Returns
        -------
        dict
            ``general_score``, ``q_movement``, ``q_collided_target``,
            ``q_avoided_target``, ``q_collided_obstacle`` and
            ``q_avoided_obstacle``.

        Examples
        --------
        >>> session = SessionStats(score_done=10, movement_done=4)
        >>> totals = session.totals(LevelStats(score=5, movement=1))
        >>> totals["general_score"], totals["q_movement"]
        (15, 5)
        """
        return {
            "general_score": self.score_done + level.score,
            "q_movement": self.movement_done + level.movement,
            "q_collided_target": self.collided_target,
            "q_avoided_target": self.avoided_target,
            "q_collided_obstacle": self.collided_obstacle,
            "q_avoided_obstacle": self.avoided_obstacle,
        }


@dataclass
class GameState:
    """Mutable state of a match.

    Attributes
    ----------
    player_id : int
        Who plays (command line argument). Defaults to 0.
    player_name : str
        First name of the player, shown under the trophy on the
        feedback screen. Defaults to "".
    professional_id : int
        Who supervises (command line argument). Defaults to 0.
    session_id : int
        Open session (0 while none was created). Defaults to 0.
    phase : int
        Phase in progress. Defaults to 1.
    level : int
        Level in progress. Defaults to 1.
    level_time : int
        Level duration (s). Defaults to 120.
    hud : bool
        Interface option (can be toggled during the game). Defaults to
        True.
    sound : bool
        Interface option (can be toggled during the game). Defaults to
        True.
    feet_marker : bool
        Draws the dot at the real feet position during the game.
        Defaults to False.
    feet_click : bool
        The feet select the menu buttons (the dot always appears in the
        menus). Defaults to False.
    lane : int
        Current lane of the player (0, 1, 2; -1 outside the area).
        Defaults to 1.
    menu : str
        Menu screen to show: "Inicial", "Pause", "Feedback_1..3".
        Defaults to "Inicial".
    time_past : float
        Game time (ms) of the level in progress. Defaults to 0.0.
    delta_time : float
        Real time (s) since the previous frame, already capped. Defaults
        to 1/60.
    targets_spawn_time : float
        Interval (s) between objects in the current level. Defaults to
        8.
    targets_move_speed : int
        Speed of the objects in the current level. Defaults to 1.
    level_stats : LevelStats
        Counters of the level in progress.
    session_stats : SessionStats
        Totals of the session.
    """

    player_id: int = 0
    player_name: str = ""
    professional_id: int = 0
    session_id: int = 0

    phase: int = 1
    level: int = 1
    level_time: int = 120

    hud: bool = True
    sound: bool = True
    feet_marker: bool = False
    feet_click: bool = False

    lane: int = 1
    menu: str = "Inicial"

    time_past: float = 0.0
    delta_time: float = 1 / 60

    targets_spawn_time: float = 8
    targets_move_speed: int = 1

    level_stats: LevelStats = field(default_factory=LevelStats)
    session_stats: SessionStats = field(default_factory=SessionStats)

    @classmethod
    def from_settings(
        cls, settings: dict, player_id: int, professional_id: int
    ) -> "GameState":
        """Create the initial state from the effective configuration.

        Parameters
        ----------
        settings : dict
            Dictionary from
            ``PlayerKarteaConfigService.build_game_settings``.
        player_id : int
            Who plays.
        professional_id : int
            Who supervises.

        Returns
        -------
        GameState
            State with phase, level, level time and interface options
            from ``settings``; ``feet_marker``/``feet_click`` default to
            False when missing.

        Examples
        --------
        >>> settings = {
        ...     "phase_id": "2", "level_id": 3, "level_time": 60,
        ...     "hud": 1, "sound": 0,
        ... }
        >>> state = GameState.from_settings(settings, 1, 2)
        >>> state.phase, state.level, state.sound, state.feet_click
        (2, 3, False, False)
        """
        return cls(
            player_id=player_id,
            professional_id=professional_id,
            phase=int(settings["phase_id"]),
            level=int(settings["level_id"]),
            level_time=int(settings["level_time"]),
            hud=bool(settings["hud"]),
            sound=bool(settings["sound"]),
            feet_marker=bool(settings.get("feet_marker", False)),
            feet_click=bool(settings.get("feet_click", False)),
        )
