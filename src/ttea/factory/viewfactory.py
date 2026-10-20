"""Access to the application and game view factories.

This module exposes the ``ViewFactory`` class, which provides static
methods for retrieving the application view factory and the view
factories of the installed games.
"""

from typing import List

from ttea.factory import AppViewFactory
from ttea.model import GameMetadata
from ttea.service import PlayerGameLaunchService


class ViewFactory:
    """Factory of factories for the application and game views.

    It is the central point for getting the application view factory
    and the view factory of each installed game.

    Attributes
    ----------
    _game_factories : dict[str, object], class attribute
        Game view factory instances (``GameViewFactoryProtocol``) by
        game ID, filled by ``discover_games``.
    _game_metadata : dict[str, GameMetadata], class attribute
        Metadata of the games that have a view factory, by game ID.

    Methods
    -------
    get_app_view_factory()
        Return the factory for application views.
    get_games_metadata()
        Return the metadata of the installed games.
    discover_games()
        Load the view factories declared by the games.
    get_game_view_factory(name)
        Return the view factory of a game.
    get_game_metadata(name)
        Return the metadata of a game with a view factory.
    """

    _game_factories = {}
    _game_metadata = {}

    @staticmethod
    def get_app_view_factory() -> AppViewFactory:
        """Return the factory for application views.

        Returns
        -------
        AppViewFactory
            A new ``AppViewFactory`` instance.
        """
        return AppViewFactory()

    @staticmethod
    def get_games_metadata() -> List[GameMetadata]:
        """Return the metadata of the installed games.

        Returns
        -------
        list[GameMetadata]
            Metadata from
            ``PlayerGameLaunchService.get_games_metadata()``.
        """
        return PlayerGameLaunchService().get_games_metadata()

    @staticmethod
    def discover_games():
        """Load the view factories declared in the game metadata.

        Notes
        -----
        For each game whose metadata has ``view_factory`` (a dotted path
        ``"package.module.ClassName"``), the module is imported, the
        class is instantiated and the instance is stored with the game
        metadata under the game ID. Games without ``view_factory`` are
        skipped. Import errors are not caught.
        """
        for metadata in ViewFactory.get_games_metadata():
            if metadata.view_factory:
                module_name, class_name = metadata.view_factory.rsplit(".", 1)
                module = __import__(module_name, fromlist=[class_name])
                factory_cls = getattr(module, class_name)
                ViewFactory._game_factories[metadata.id] = factory_cls()
                ViewFactory._game_metadata[metadata.id] = metadata

    @staticmethod
    def get_game_view_factory(name: str):
        """Return the view factory of a game.

        Parameters
        ----------
        name : str
            Game ID, e.g. ``"br.udesc.larva.kartea"``.

        Returns
        -------
        GameViewFactoryProtocol
            The factory instance created by ``discover_games``.

        Raises
        ------
        KeyError
            If no factory was loaded for ``name``.
        """
        return ViewFactory._game_factories[name]

    @staticmethod
    def get_game_metadata(name: str):
        """Return the metadata of a game loaded by ``discover_games``.

        Parameters
        ----------
        name : str
            Game ID.

        Returns
        -------
        GameMetadata | None
            The metadata, or None if the game has no loaded factory.
        """
        return ViewFactory._game_metadata.get(name)
