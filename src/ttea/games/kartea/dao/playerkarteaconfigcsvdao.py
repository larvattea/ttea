"""CSV DAO of the players' Kartea game configuration."""

from ttea.dao.playercsvdao import PlayerCsvDAO
from ttea.games.kartea.model import (
    KarteaPhase,
    KarteaPhaseLevel,
    PlayerKarteaConfig,
)

from .basecsvdao import BaseCsvDAO
from .karteaphasecsvdao import KarteaPhaseCsvDAO
from .karteaphaselevelcsvdao import KarteaPhaseLevelCsvDAO
from .playerkarteasessioncsvdao import PlayerKarteaSessionCsvDAO


class PlayerKarteaConfigCsvDAO(BaseCsvDAO[PlayerKarteaConfig]):
    """DAO of PlayerKarteaConfig in CSV.

    Each player has a file
    ``{player_id}_{sanitized_name}_kartea_config.csv`` with a single
    row; the configuration key is the player id. The CRUD lives in
    BaseCsvDAO; this class only builds the references (player, session,
    phase and level).

    Attributes
    ----------
    model : type, class attribute
        PlayerKarteaConfig.
    suffix : str, class attribute
        "kartea_config".
    single_row : bool, class attribute
        True: one row per player, keyed by the player id.
    configs : dict[int, PlayerKarteaConfig]
        Configurations by player id (the same dictionary as ``cache``).
    player_dao : PlayerCsvDAO
        DAO for accessing Player objects.
    session_dao : PlayerKarteaSessionCsvDAO
        DAO for accessing PlayerKarteaSession objects.
    phase_dao : KarteaPhaseCsvDAO
        DAO for accessing KarteaPhase objects.
    level_dao : KarteaPhaseLevelCsvDAO
        DAO for accessing KarteaPhaseLevel objects (shares
        ``phase_dao``).

    See Also
    --------
    KarteaPhaseService : Lists of phases and levels.

    Notes
    -----
    Creating the DAO creates the auxiliary DAOs and then loads the
    configurations.
    """

    model = PlayerKarteaConfig
    suffix = "kartea_config"
    single_row = True

    def __init__(self) -> None:
        self.player_dao = PlayerCsvDAO()
        self.session_dao = PlayerKarteaSessionCsvDAO()
        self.phase_dao = KarteaPhaseCsvDAO()
        self.level_dao = KarteaPhaseLevelCsvDAO(phase_dao=self.phase_dao)

        super().__init__()  # loads the configs; needs the DAOs above

    def get_phase(self, phase_id: int) -> KarteaPhase | None:
        """Retrieve a KarteaPhase by its ID using phase_dao.

        Parameters
        ----------
        phase_id : int
            The ID of the phase to retrieve.

        Returns
        -------
        KarteaPhase | None
            The KarteaPhase object if found, None otherwise.
        """
        return self.phase_dao.select(phase_id)

    def get_level(
        self, phase_id: int, level_id: int
    ) -> KarteaPhaseLevel | None:
        """Retrieve a KarteaPhaseLevel by phase and level ID.

        Parameters
        ----------
        phase_id : int
            The ID of the phase the level belongs to.
        level_id : int
            The ID of the level within the phase.

        Returns
        -------
        KarteaPhaseLevel | None
            The KarteaPhaseLevel object if found, None otherwise.
        """
        return self.level_dao.select(phase_id, level_id)

    @property
    def configs(self) -> dict[int, PlayerKarteaConfig]:
        """Configurations by player id (the ``cache`` dictionary)."""
        return self.cache

    def load_all_configs(self) -> None:
        """Load all configuration files into the cache."""
        self.load_all()

    @staticmethod
    def _int_or_none(value: str | None) -> int | None:
        """Convert a CSV cell to int (None if not digits only)."""
        value = (value or "").strip()
        return int(value) if value.isdigit() else None

    def _deserialize(
        self, row: dict[str, str], player_id: int
    ) -> PlayerKarteaConfig | None:
        """Build the configuration with its references.

        Resolves player, session, phase and level.

        Parameters
        ----------
        row : dict[str, str]
            CSV row of the configuration.
        player_id : int
            Player id taken from the file name.

        Returns
        -------
        PlayerKarteaConfig | None
            The configuration, or None if the player does not exist (the
            file is ignored).

        Notes
        -----
        - Empty, zero or unknown session, phase or level ids become
          None.
        - A level that does not belong to the phase (or without a phase)
          is discarded.
        """
        player = self.player_dao.select(player_id)
        if not player:
            return None

        session_id = self._int_or_none(row.get("session"))
        session = self.session_dao.select(session_id) if session_id else None

        phase = level = None
        phase_id = self._int_or_none(row.get("phase"))
        if phase_id:
            phase = self.get_phase(phase_id)
            level_id = self._int_or_none(row.get("level"))
            if level_id:
                level = self.get_level(phase_id, level_id)
                if level and (not phase or level.phase.id != phase.id):
                    level = None  # Ensure level belongs to phase

        return PlayerKarteaConfig(
            player=player,
            session=session,
            phase=phase,
            level=level,
            **self._plain_kwargs(row, skip=self.model.REF_PROPERTIES),
        )
