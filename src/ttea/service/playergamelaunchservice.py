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
        """Read the metadata of each installed game.

        Returns
        -------
        list[GameMetadata]
            Metadata of the folder games, in folder name order, followed
            by the ``.ttea`` cartridges, in file name order.

        Notes
        -----
        Every subfolder of ``PathConfig.EXERGAME_DIR`` that has a
        ``metadata.json`` is read, and so is the ``manifest.json`` of
        every ``.ttea`` file there. Games with invalid metadata
        (``ValueError``) are skipped and the reason is logged as a
        warning; other errors (e.g. ``OSError``) are not caught. A
        cartridge whose ID is already used by a folder game or an
        earlier cartridge is skipped with a warning.
        """
        from ttea.log import Log

        games = []
        cartridges = []
        exergame_dir = PathConfig.EXERGAME_DIR

        for d in sorted(exergame_dir.iterdir()):
            meta_path = d / PlayerGameLaunchService.METADATA_FILENAME
            if d.is_dir() and meta_path.exists():
                try:
                    games.append(GameMetadata.load(meta_path))
                except ValueError as e:
                    Log.get_log().log_warning(f"Jogo ignorado: {e}")
            elif (
                d.is_file()
                and d.suffix.lower() == GameMetadata.CARTRIDGE_EXTENSION
            ):
                try:
                    cartridges.append(GameMetadata.load_cartridge(d))
                except ValueError as e:
                    Log.get_log().log_warning(f"Jogo ignorado: {e}")

        ids = {g.id for g in games}
        for c in cartridges:
            if c.id in ids:
                Log.get_log().log_warning(
                    f"Jogo ignorado: {c.entrypoint_path}: id '{c.id}' "
                    f"já usado por outro jogo"
                )
            else:
                ids.add(c.id)
                games.append(c)
        return games
