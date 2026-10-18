"""Service of the events of the players' Kartea game sessions."""

from ttea.games.kartea.dao import PlayerKarteaSessionDetailCsvDAO
from ttea.games.kartea.model import PlayerKarteaSessionDetail

from .csvcrudservice import CsvCrudService


class PlayerKarteaSessionDetailService(
    CsvCrudService[PlayerKarteaSessionDetail]
):
    """Session events (one row per event). See CsvCrudService.

    Attributes
    ----------
    model : type, class attribute
        PlayerKarteaSessionDetail.
    dao_class : type, class attribute
        PlayerKarteaSessionDetailCsvDAO.
    create_player_kartea_session_detail : function, class attribute
        Alias of ``CsvCrudService.create``, the name used by
        SessionRecorder.
    update_player_kartea_session_detail : function, class attribute
        Alias of ``CsvCrudService.update``, the name used by
        SessionRecorder.
    """

    model = PlayerKarteaSessionDetail
    dao_class = PlayerKarteaSessionDetailCsvDAO

    # Names used by SessionRecorder
    create_player_kartea_session_detail = CsvCrudService.create
    update_player_kartea_session_detail = CsvCrudService.update
