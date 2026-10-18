"""CSV DAO of the events of the players' Kartea game sessions."""

from ttea.games.kartea.model import PlayerKarteaSessionDetail

from .basecsvdao import BaseCsvDAO
from .playerkarteasessioncsvdao import PlayerKarteaSessionCsvDAO


class PlayerKarteaSessionDetailCsvDAO(BaseCsvDAO[PlayerKarteaSessionDetail]):
    """DAO of PlayerKarteaSessionDetail (session events) in CSV.

    All events of a player are stored in
    ``{player_id}_{sanitized_name}_kartea_session_detail.csv``, one row
    per event, with an incremental id. Each event is appended to the end
    of the file. The CRUD lives in BaseCsvDAO.

    Parameters
    ----------
    session_dao : PlayerKarteaSessionCsvDAO | None, optional
        Shared session DAO (the same as the configuration service's). If
        None, the DAO creates its own.

    Attributes
    ----------
    model : type, class attribute
        PlayerKarteaSessionDetail.
    suffix : str, class attribute
        "kartea_session_detail".
    session_dao : PlayerKarteaSessionCsvDAO
        Session DAO (resolves the "session" column).
    details : dict[int, PlayerKarteaSessionDetail]
        Events by id (the same dictionary as ``cache``).
    """

    model = PlayerKarteaSessionDetail
    suffix = "kartea_session_detail"

    def __init__(
        self, session_dao: PlayerKarteaSessionCsvDAO | None = None
    ) -> None:
        self.session_dao = session_dao or PlayerKarteaSessionCsvDAO()
        super().__init__()

    @property
    def details(self) -> dict[int, PlayerKarteaSessionDetail]:
        """Events by id (the same dictionary as ``cache``)."""
        return self.cache

    def load_all_details(self) -> None:
        """Load all session detail files into the cache."""
        self.load_all()

    def _player(self, obj: PlayerKarteaSessionDetail):
        """Return the player of the event's session (or None)."""
        return obj.session.player if obj.session else None

    def _deserialize(
        self, row: dict[str, str], player_id: int
    ) -> PlayerKarteaSessionDetail | None:
        """Build the event from a CSV row.

        Parameters
        ----------
        row : dict[str, str]
            CSV row of the event.
        player_id : int
            Player id taken from the file name (not used).

        Returns
        -------
        PlayerKarteaSessionDetail | None
            The event, with ``session`` resolved by ``session_dao``
            (None if the session does not exist). ``event_type`` keeps
            the CSV text.
        """
        return PlayerKarteaSessionDetail(
            id=self._to_int(row.get("id")),
            session=self.session_dao.select(self._to_int(row.get("session"))),
            **self._plain_kwargs(row, skip=("id", "session")),
        )
