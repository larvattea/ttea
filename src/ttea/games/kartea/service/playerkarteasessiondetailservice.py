from typing import Any, Dict, Optional

from ttea.games.kartea.dao import PlayerKarteaSessionDetailCsvDAO
from ttea.games.kartea.model import PlayerKarteaSessionDetail


class PlayerKarteaSessionDetailService:

    def __init__(
        self,
        dao: Optional[PlayerKarteaSessionDetailCsvDAO] = None,
    ):
        self.dao = dao or PlayerKarteaSessionDetailCsvDAO()

    def create_player_kartea_session_detail(
        self, data: Dict[str, Any]
    ) -> Optional[PlayerKarteaSessionDetail]:
        playerkarteasessiondetail = PlayerKarteaSessionDetail(**data)

        new_id = self.dao.insert(playerkarteasessiondetail)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_player_kartea_session_detail(
        self, playerkarteasessiondetail_id: int, data: Dict[str, Any]
    ) -> bool:
        playerkarteasessiondetail = self.dao.select(
            playerkarteasessiondetail_id
        )
        if not playerkarteasessiondetail:
            return False

        playerkarteasessiondetail.set_data(data)

        success = self.dao.update(playerkarteasessiondetail)

        return success

    def find_by_id(
        self, playerkarteasessiondetail_id: int
    ) -> Optional[PlayerKarteaSessionDetail]:
        return self.dao.select(playerkarteasessiondetail_id)
