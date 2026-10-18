"""CSV DAO of the players' Kartea game sessions."""

from ttea.dao import PlayerCsvDAO
from ttea.games.kartea.model import PlayerKarteaSession

from .basecsvdao import BaseCsvDAO


class PlayerKarteaSessionCsvDAO(BaseCsvDAO[PlayerKarteaSession]):
    """DAO of PlayerKarteaSession in CSV.

    All sessions of a player are stored in
    ``{player_id}_{sanitized_name}_kartea_session.csv``, one row per
    session, with an incremental id. The CRUD lives in BaseCsvDAO.

    Attributes
    ----------
    model : type, class attribute
        PlayerKarteaSession.
    suffix : str, class attribute
        "kartea_session".
    player_dao : PlayerCsvDAO
        DAO for accessing Player objects.
    sessions : dict[int, PlayerKarteaSession]
        Sessions by id (the same dictionary as ``cache``).
    """

    model = PlayerKarteaSession
    suffix = "kartea_session"

    def __init__(self) -> None:
        self.player_dao = PlayerCsvDAO()
        super().__init__()

    @property
    def sessions(self) -> dict[int, PlayerKarteaSession]:
        """Sessions by id (the same dictionary as ``cache``)."""
        return self.cache

    def load_all_sessions(self) -> None:
        """Load all session files into the cache."""
        self.load_all()

    def _is_valid(self, obj: PlayerKarteaSession) -> bool:
        """Validate the session: valid player and valid professional."""
        return super()._is_valid(obj) and bool(
            obj.professional and obj.professional.is_valid()
        )

    def _deserialize(
        self, row: dict[str, str], player_id: int
    ) -> PlayerKarteaSession | None:
        """Build the session from a CSV row.

        Parameters
        ----------
        row : dict[str, str]
            CSV row of the session.
        player_id : int
            Player id taken from the file name.

        Returns
        -------
        PlayerKarteaSession | None
            The session, with ``player`` resolved by ``player_dao``.

        Notes
        -----
        ``professional`` is not resolved to an object: it keeps the id
        text read from the CSV (written back as is by ``get_data``).
        """
        return PlayerKarteaSession(
            id=self._to_int(row.get("id")),
            player=self.player_dao.select(player_id),
            **self._plain_kwargs(row, skip=("id", "player")),
        )
