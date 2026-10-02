from ttea.sdk.library import Library, catalog, localized, resolve_release
from typing import List

# Local module import
from ttea.model import Player, Professional


class PlayerGameLaunchService:

    def __init__(self):
        from ttea.service import PlayerService, ProfessionalService

        self.player_service = PlayerService()
        self.professional_service = ProfessionalService()
        self.library = Library()

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

    def get_games_metadata(self) -> List[dict]:
        games = {game["id"]: dict(game) for game in catalog()}
        for receipt in self.library.installed():
            manifest = receipt["manifest"]
            game = games.setdefault(manifest["id"], {"id": manifest["id"], "releases": []})
            game["installed"] = True
            game["version"] = manifest["version"]
            game["game"] = manifest["id"]
            game["language"] = {
                locale.replace("-", "_"): {"name": name, "description": localized(manifest.get("description", {}), locale, "")}
                for locale, name in manifest["name"].items()
            }
        for game in games.values():
            game["release"] = resolve_release(game)
        return list(games.values())

    def install_game(self, game):
        return self.library.install_release(game, update=bool(game.get("installed")))

    def uninstall_game(self, game):
        self.library.uninstall(game["id"])

    def launch_game(self, game, config):
        return self.library.launch(game["id"], config=config)
