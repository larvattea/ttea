from typing import Any, Dict, Optional

from ttea.games.kartea.dao import PlayerKarteaSessionCsvDAO
from ttea.games.kartea.model import PlayerKarteaSession


class PlayerKarteaSessionService:

    def __init__(
        self,
        dao: Optional[PlayerKarteaSessionCsvDAO] = None,
    ):
        self.dao = dao or PlayerKarteaSessionCsvDAO()

    def create_player_kartea_session(
        self, data: Dict[str, Any]
    ) -> Optional[PlayerKarteaSession]:
        playerkarteasession = PlayerKarteaSession(**data)

        new_id = self.dao.insert(playerkarteasession)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_player_kartea_session(
        self, playerkarteasession_id: int, data: Dict[str, Any]
    ) -> bool:
        playerkarteasession = self.dao.select(playerkarteasession_id)
        if not playerkarteasession:
            return False

        playerkarteasession.set_data(data)

        success = self.dao.update(playerkarteasession)

        return success

    def find_by_id(
        self, playerkarteasession_id: int
    ) -> Optional[PlayerKarteaSession]:
        return self.dao.select(playerkarteasession_id)
