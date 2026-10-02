"""Compatibility with the console's existing KarTEA participant CSV records."""
from dataclasses import fields

from ttea.games.kartea.model import PlayerKarteaConfig
from ttea.games.kartea.service import (
    PlayerKarteaConfigService, PlayerKarteaSessionService,
    PlayerKarteaSessionDetailService,
)

_OWNERSHIP_FIELDS = {"player", "session", "update_session_id", "phase", "level"}
_SETTING_KEYS = frozenset(
    {f.name for f in fields(PlayerKarteaConfig) if f.name not in _OWNERSHIP_FIELDS}
    | {"phase_id", "level_id"})


class KarteaRecords:
    def __init__(self, player_id: int, professional_id: int):
        self._configs = PlayerKarteaConfigService()
        self._sessions = PlayerKarteaSessionService()
        self._events = PlayerKarteaSessionDetailService()
        self._player = self._configs.player_service.find_by_id(player_id)
        self._professional = self._configs.professional_service.find_by_id(professional_id)
        if self._player is None or self._professional is None:
            raise ValueError("Registered KarTEA sessions require a known player and professional")
        self._active = {}

    def configuration(self, defaults: dict) -> dict:
        config = self._configs.find_config_by_player_id(self._player.id)
        if config is None:
            config = self._configs.create_config({**defaults, "player_id": self._player.id})
        if config is None:
            raise ValueError("Unable to create KarTEA player configuration")
        result = {f.name: getattr(config, f.name) for f in fields(config)
                  if f.name not in {"player", "session", "phase", "level"}}
        result.update(phase_id=config.phase.id, level_id=config.level.id)
        return result

    def update_configuration(self, values: dict) -> None:
        foreign = set(values) - _SETTING_KEYS - {"session_id"}
        if foreign:
            raise ValueError(f"KarTEA configuration rejects non-setting keys: {sorted(foreign)}")
        if "session_id" in values and values["session_id"] not in self._active:
            raise ValueError("KarTEA configuration may only reference a session started by this game")
        if not self._configs.update_config(self._player.id, values):
            raise OSError("Unable to update KarTEA player configuration")

    def start_session(self, values: dict) -> int:
        session = self._sessions.create_player_kartea_session(
            {**values, "id": 0, "player": self._player, "professional": self._professional})
        if session is None:
            raise OSError("Unable to create KarTEA CSV session")
        self._active[session.id] = session
        return session.id

    def update_session(self, session_id: int, values: dict) -> None:
        session = self._active[session_id]
        if not self._sessions.update_player_kartea_session(session.id, values):
            raise OSError("Unable to update KarTEA CSV session")

    def record_event(self, session_id: int, values: dict) -> None:
        session = self._active[session_id]
        if self._events.create_player_kartea_session_detail(
                {**values, "id": 0, "session": session}) is None:
            raise OSError("Unable to write KarTEA CSV event")
