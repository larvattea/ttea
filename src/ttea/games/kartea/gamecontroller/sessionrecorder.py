"""Recording of the game session (session, details and configuration).

Attributes
----------
DATE_FORMAT : str
    ISO 8601 date format used in all records ("%Y-%m-%d").
TIME_FORMAT : str
    ISO 8601 time format used in all records ("%H:%M:%S").
"""

import time
from datetime import datetime
from typing import TYPE_CHECKING

from ttea.games.kartea.model import PlayerKarteaSessionDetail

if TYPE_CHECKING:
    from ttea.games.kartea.gameutil import GameState
    from ttea.games.kartea.model import PlayerKarteaSession
    from ttea.games.kartea.service import (
        PlayerKarteaConfigService,
        PlayerKarteaSessionDetailService,
        PlayerKarteaSessionService,
    )

EventType = PlayerKarteaSessionDetail.EventType

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


def utc_offset(moment: datetime) -> str:
    """Return the UTC offset of the local time in ISO 8601.

    Parameters
    ----------
    moment : datetime
        Moment whose offset is taken, in the computer's local time zone.

    Returns
    -------
    str
        Offset such as "-03:00", or "" if it cannot be determined.
    """
    offset = moment.astimezone().strftime("%z")  # e.g. "-0300"
    return f"{offset[:3]}:{offset[3:]}" if offset else ""


class SessionRecorder:
    """Persist the match: session row, events (details) and config.

    Reads the GameState and writes through the services; it does not
    decide game rules. Session, configuration and detail go together:
    the session's phase_reached/level_reached and the kartea_config
    phase/level receive the current phase/level, the same as the events
    recorded in the detail.

    Parameters
    ----------
    state : GameState
        Match state (source of the recorded values).
    config_service : PlayerKarteaConfigService
        Player/professional lookup and recording of phase/level/session
        in the configuration.
    session_service : PlayerKarteaSessionService
        Sessions (must share the config_service session DAO, so that the
        session created here is recorded in kartea_config).
    session_detail_service : PlayerKarteaSessionDetailService
        Events (details) of the session.

    Attributes
    ----------
    AUTOSAVE_INTERVAL : float, class attribute
        Interval (real seconds) between automatic session saves (30).
    SESSION_TOTAL_BY_EVENT : dict[EventType, str], class attribute
        Detail event -> session total (SessionStats) it increments.
    state : GameState
        Match state.
    config_service : PlayerKarteaConfigService
        Configuration service.
    session_service : PlayerKarteaSessionService
        Session service.
    session_detail_service : PlayerKarteaSessionDetailService
        Session detail service.
    current_session : PlayerKarteaSession | None
        Open session; None until the first event.
    start_date, start_time : str | None
        Start of the session (DATE_FORMAT / TIME_FORMAT).
    last_save : float
        Time of the last session save (``time.time()``).
    """

    AUTOSAVE_INTERVAL = 30.0

    SESSION_TOTAL_BY_EVENT = {
        EventType.COLLIDED_TARGET: "collided_target",
        EventType.AVOIDED_TARGET: "avoided_target",
        EventType.COLLIDED_OBSTACLE: "collided_obstacle",
        EventType.AVOIDED_OBSTACLE: "avoided_obstacle",
    }

    def __init__(
        self,
        state: "GameState",
        config_service: "PlayerKarteaConfigService",
        session_service: "PlayerKarteaSessionService",
        session_detail_service: "PlayerKarteaSessionDetailService",
    ):
        self.state = state
        self.config_service = config_service
        self.session_service = session_service
        self.session_detail_service = session_detail_service

        self.current_session: PlayerKarteaSession | None = None
        self.start_date: str | None = None
        self.start_time: str | None = None
        self.last_save = time.time()

    @property
    def has_session(self) -> bool:
        """Whether a session is already open."""
        return self.current_session is not None

    # ======================
    # Events
    # ======================
    def record(
        self, event_type: EventType | str, event_position: int = 0
    ) -> None:
        """Record an event (opening the session on the first event).

        Parameters
        ----------
        event_type : EventType | str
            Type of the event.
        event_position : int, optional
            Lane related to the event (0 when it has none).

        Notes
        -----
        Collision/avoidance events also add to the session totals
        (SessionStats), at this single point. The event gets the current
        date/time, phase, level and player lane.
        """
        if self.current_session is None:
            self._create_session()

        total_key = self.SESSION_TOTAL_BY_EVENT.get(event_type)
        if total_key is not None:
            stats = self.state.session_stats
            setattr(stats, total_key, getattr(stats, total_key) + 1)

        now = datetime.now()
        self.session_detail_service.create_player_kartea_session_detail(
            {
                "id": 0,
                "session": self.current_session,
                "event_date": now.strftime(DATE_FORMAT),
                "event_time": now.strftime(TIME_FORMAT),
                "phase": self.state.phase,
                "level": self.state.level,
                "player_position": self.state.lane,
                "event_position": event_position,
                "event_type": event_type,
            }
        )

    # ======================
    # Session
    # ======================
    def save(self) -> None:
        """Save the session row and the phase/level in the config.

        The session row gets the totals up to this moment. Called at the
        end of each level, after every phase/level change and at the
        checkpoints (pause, menu choices, game exit and autosave), so
        that an interrupted level also reaches the session.

        Notes
        -----
        The configuration follows the game (advance, regress...): the
        next session starts where this one stopped. It is updated even
        when no session is open.
        """
        if self.current_session is not None:
            now = datetime.now()
            self.session_service.update_player_kartea_session(
                self.current_session.id,
                {
                    "end_date": now.strftime(DATE_FORMAT),
                    "end_time": now.strftime(TIME_FORMAT),
                    **self._totals_data(),
                },
            )
            self.last_save = time.time()
        self.config_service.update_config_level(
            self.state.player_id, self.state.phase, self.state.level
        )

    def autosave_if_due(self) -> None:
        """Save the session if AUTOSAVE_INTERVAL has passed."""
        if time.time() - self.last_save >= self.AUTOSAVE_INTERVAL:
            self.save()

    def _totals_data(self) -> dict:
        """Return the whole session totals (never reset per level)."""
        return {
            "phase_reached": self.state.phase,
            "level_reached": self.state.level,
            **self.state.session_stats.totals(self.state.level_stats),
        }

    def _create_session(self) -> None:
        """Create the session row and record it in the configuration.

        Notes
        -----
        The session id is copied to ``GameState.session_id`` and saved
        in the player's configuration only if it allows it
        (``update_session_id``).
        """
        now = datetime.now()
        self.start_date = now.strftime(DATE_FORMAT)
        self.start_time = now.strftime(TIME_FORMAT)

        self.current_session = (
            self.session_service.create_player_kartea_session(
                {
                    "id": 0,
                    "player": self.config_service.find_player(
                        self.state.player_id
                    ),
                    "professional": self.config_service.find_professional(
                        self.state.professional_id
                    ),
                    "start_date": self.start_date,
                    "start_time": self.start_time,
                    "end_date": now.strftime(DATE_FORMAT),
                    "end_time": now.strftime(TIME_FORMAT),
                    **self._totals_data(),
                    "utc_offset": utc_offset(now),
                }
            )
        )

        if self.current_session:
            self.state.session_id = self.current_session.id
            self.config_service.update_config_session(
                self.state.player_id, self.current_session.id
            )
