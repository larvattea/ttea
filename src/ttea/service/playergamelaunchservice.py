"""Service of the game launch screen: players, professionals, games."""

from typing import List

from ttea.model import GameMetadata, Player, Professional
from ttea.util import PathConfig


class PlayerGameLaunchService:
    """Provide the data of the game launch screen.

    Attributes
    ----------
    METADATA_FILENAME : str, class attribute
        Name of the metadata file of each game (``metadata.json``).
    player_service : PlayerService
        Player service.
    professional_service : ProfessionalService
        Professional service.
    """

    METADATA_FILENAME = GameMetadata.FILENAME

    def __init__(self):
        from ttea.service import PlayerService, ProfessionalService

        self.player_service = PlayerService()
        self.professional_service = ProfessionalService()

    def get_all_players(self) -> List[Player]:
        """Return all players sorted by name.

        Returns
        -------
        list[Player]
            Players sorted by ``name`` (case-sensitive).
        """
        return sorted(
            self.player_service.get_all_players(),
            key=lambda p: p.name,
        )

    def get_all_professionals(self) -> List[Professional]:
        """Return all professionals sorted by name.

        Returns
        -------
        list[Professional]
            Professionals sorted by ``name`` (case-sensitive).
        """
        return sorted(
            self.professional_service.get_all_professionals(),
            key=lambda h: h.name,
        )

    def get_games_metadata(self) -> List[GameMetadata]:
        """Read the ``metadata.json`` of each installed game.

        Returns
        -------
        list[GameMetadata]
            Metadata of the games, in folder name order.

        Notes
        -----
        Every subfolder of ``PathConfig.EXERGAME_DIR`` that has a
        ``metadata.json`` is read. Games with invalid metadata
        (``ValueError``) are skipped and the reason is logged as a
        warning; other errors (e.g. ``OSError``) are not caught.
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
