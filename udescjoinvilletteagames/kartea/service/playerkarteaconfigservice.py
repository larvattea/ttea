from typing import Any, Dict, List, Optional, Union

from udescjoinvilletteagames.kartea.dao import PlayerKarteaConfigCsvDAO
from udescjoinvilletteagames.kartea.model import (
    KarteaPhase,
    KarteaPhaseLevel,
    PlayerKarteaConfig,
)


class PlayerKarteaConfigService:
    """
    Service layer for PlayerKarteaConfig operations (MVCS pattern).
    Handles business logic and delegates to DAO.
    """

    def __init__(self, dao: Optional[PlayerKarteaConfigCsvDAO] = None):
        """
        Initialize with a DAO (injectable for testing).
        """
        self.dao = dao or PlayerKarteaConfigCsvDAO()

    def get_all_configs(self) -> List[PlayerKarteaConfig]:
        """Return all PlayerKarteaConfig instances."""
        return self.dao.list()

    def create_config(
        self, data: Dict[str, Any]
    ) -> Optional[PlayerKarteaConfig]:
        """
        Create a new config from data dict.
        Validates and inserts via DAO.
        """
        # Resolve references (e.g., fetch Player, Phase, Level from DAO)
        player = self.dao.player_dao.select(data.get("player_id"))
        session = self.dao.session_dao.select(data.get("session_id"))
        phase = self.dao.phase_dao.select(data.get("phase_id"))
        level = self.dao.level_dao.select(data.get("level_id"))

        if not player or not phase or not level:
            return None  # Invalid references

        config = PlayerKarteaConfig(
            player=player,
            session=session,
            phase=phase,
            level=level,
            level_time=data.get("level_time", 0),
            car_image=data.get("car_image", ""),
            environment_image=data.get("environment_image", ""),
            target_image=data.get("target_image", ""),
            obstacle_image=data.get("obstacle_image", ""),
            positive_feedback_image=data.get("positive_feedback_image", ""),
            neutral_feedback_image=data.get("neutral_feedback_image", ""),
            negative_feedback_image=data.get("negative_feedback_image", ""),
            positive_feedback_sound=data.get("positive_feedback_sound", ""),
            neutral_feedback_sound=data.get("neutral_feedback_sound", ""),
            negative_feedback_sound=data.get("negative_feedback_sound", ""),
            palette=data.get("palette", 0),
            hud=data.get("hud", False),
            sound=data.get("sound", False),
        )

        if not self.is_valid_config(config):  # Add custom validation if needed
            return None

        player_id = self.dao.insert(config)
        return self.dao.select(player_id) if player_id else None

    def update_config(self, player_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing config.
        """
        config = self.dao.select(player_id)
        if not config:
            return False

        # Update fields (similar to create, resolve references)
        config.level_time = data.get("level_time", config.level_time)
        # ... Update other fields similarly ...

        if not self.is_valid_config(config):
            return False

        return self.dao.update(config)

    def delete_config(self, player_id: int) -> bool:
        """Delete a config by player ID."""
        return self.dao.delete(player_id)

    def find_by_player_id(
        self, player_id: int
    ) -> Optional[PlayerKarteaConfig]:
        """Find config by player ID."""
        return self.dao.select(player_id)

    def search_configs(self, query: str = "") -> List[PlayerKarteaConfig]:
        """
        Search configs by player name or ID.
        """
        all_configs = self.get_all_configs()
        if not query.strip():
            return all_configs

        q = query.lower().strip()
        return [
            c
            for c in all_configs
            if q in str(c.player.id)
            or (c.player and q in c.player.name.lower())
        ]

    def is_valid_config(self, config: PlayerKarteaConfig) -> bool:
        """Custom validation (expand as needed)."""
        # Example: Check required fields
        return bool(config.player and config.phase and config.level)

    def get_phase(self, phase_id: int) -> Optional[KarteaPhase]:
        return self.dao.get_phase(phase_id)

    # Additional methods from DAO if needed
    def get_all_phases(self) -> List[KarteaPhase]:
        return self.dao.get_all_phases()

    def get_levels_for_phase(
        self, phase: Union[int, KarteaPhase]
    ) -> List[KarteaPhaseLevel]:
        return self.dao.get_levels_for_phase(phase)
