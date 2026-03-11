import json
from typing import TYPE_CHECKING, List, Optional

# Local module import
from udescjoinvilletteamodel import Language, Player
from udescjoinvilletteautil import PathConfig

if TYPE_CHECKING:
    from udescjoinvilletteaservice import PlayerService


class PlayerGameLaunchService:
    METADATA_FILENAME = "metadata.json"

    def __init__(self, player_service: Optional["PlayerService"] = None):
        from udescjoinvilletteaservice import PlayerService

        self.player_service = player_service or PlayerService()

    def get_all_players(self) -> List[Player]:
        return sorted(
            self.player_service.get_all_players(),
            key=lambda p: p.name,
        )

    def get_games_metadata(self) -> List[dict]:
        games = []
        exergame_dir = PathConfig.EXERGAME_DIR

        for d in exergame_dir.iterdir():
            if d.is_dir():
                meta_path = d / PlayerGameLaunchService.METADATA_FILENAME
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["folder_path"] = str(d)  # Guarda o caminho real
                        games.append(data)
        return games
