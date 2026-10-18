"""Factory accessors for application and game view factories.

This module exposes the ViewFactory class, which provides static methods
for retrieving application-specific and game-specific view factory
instances.
"""

from typing import List

from ttea.factory import AppViewFactory
from ttea.model import GameMetadata
from ttea.service import PlayerGameLaunchService


class ViewFactory:
    """
    Factory of factories for creating view instances for app and games modules.

    This class provides static methods to obtain factory instances
    for application views and game-specific views.
    It serves as a central point for accessing
    different view factories in the application.

    Methods
    -------
    get_app_view_factory()
        Return the factory for application views.
    get_kartea_view_factory()
        Return the factory for Kartea-related views.
    """

    _game_factories = {}
    _game_metadata = {}

    @staticmethod
    def get_app_view_factory() -> AppViewFactory:
        """
        Return the factory for application views.

        Returns
        -------
        AppViewFactory
            An instance of AppViewFactory for creating application-specific
            views.
        """
        return AppViewFactory()

    @staticmethod
    def get_games_metadata() -> List[GameMetadata]:
        return PlayerGameLaunchService().get_games_metadata()

    @staticmethod
    def discover_games():
        """Carrega fábricas dinamicamente a partir dos metadados."""
        for metadata in ViewFactory.get_games_metadata():
            if metadata.view_factory:
                module_name, class_name = metadata.view_factory.rsplit(".", 1)
                module = __import__(module_name, fromlist=[class_name])
                factory_cls = getattr(module, class_name)
                ViewFactory._game_factories[metadata.id] = factory_cls()
                ViewFactory._game_metadata[metadata.id] = metadata

    @staticmethod
    def get_game_view_factory(name: str):
        return ViewFactory._game_factories[name]

    @staticmethod
    def get_game_metadata(name: str):
        return ViewFactory._game_metadata.get(name)
