"""Service of the players' Kartea game sessions."""

from ttea.games.kartea.dao import PlayerKarteaSessionCsvDAO
from ttea.games.kartea.model import PlayerKarteaSession

from .csvcrudservice import CsvCrudService


class PlayerKarteaSessionService(CsvCrudService[PlayerKarteaSession]):
    """Game sessions (one row per session). See CsvCrudService.

    Attributes
    ----------
    model : type, class attribute
        PlayerKarteaSession.
    dao_class : type, class attribute
        PlayerKarteaSessionCsvDAO.
    create_player_kartea_session : function, class attribute
        Alias of ``CsvCrudService.create``, the name used by
        SessionRecorder.
    update_player_kartea_session : function, class attribute
        Alias of ``CsvCrudService.update``, the name used by
        SessionRecorder.
    """

    model = PlayerKarteaSession
    dao_class = PlayerKarteaSessionCsvDAO

    # Names used by SessionRecorder
    create_player_kartea_session = CsvCrudService.create
    update_player_kartea_session = CsvCrudService.update
