from typing import List

# Local module import
from ttea.model import GameMetadata, Player, Professional
from ttea.util import PathConfig


class PlayerGameLaunchService:
    METADATA_FILENAME = GameMetadata.FILENAME

    def __init__(self):
        from ttea.service import PlayerService, ProfessionalService

        self.player_service = PlayerService()
        self.professional_service = ProfessionalService()

    def get_all_players(self) -> List[Player]:
        return sorted(
            self.player_service.get_all_players(),
            key=lambda p: p.name,
        )

    def get_all_professionals(self) -> List[Professional]:
        return sorted(
            self.professional_service.get_all_professionals(),
            key=lambda h: h.name,
        )

    def get_games_metadata(self) -> List[GameMetadata]:
        """Lê o metadata.json de cada jogo instalado.

        Jogos com metadados inválidos são ignorados e o motivo é
        registrado no log.
        """
        from ttea.log import Log

        games = []
        exergame_dir = PathConfig.EXERGAME_DIR

        for d in sorted(exergame_dir.iterdir()):
            meta_path = d / PlayerGameLaunchService.METADATA_FILENAME
            if d.is_dir() and meta_path.exists():
                try:
                    games.append(GameMetadata.load(meta_path))
                except ValueError as e:
                    Log.get_log().log_warning(f"Jogo ignorado: {e}")
        return games
