"""Interface that the view factory of each game must provide."""

from typing import Callable, Optional, Protocol

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog


class GameViewFactoryProtocol(Protocol):
    """Structural interface of a game view factory.

    A game declares its factory class in ``metadata.json``
    (``runtime.view_factory``); ``ViewFactory.discover_games`` creates
    an instance of it.
    """

    @staticmethod
    def create_player_config_edit_view(
        parent: Optional[QDialog] = None, config: Optional[object] = None
    ):
        """Create the view that edits a player's game configuration.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.
        config : object | None, optional
            Configuration to edit; None creates a new one. Default is
            None.

        Returns
        -------
        object
            The edit view created by the game.
        """
        ...

    @staticmethod
    def create_player_config_list_view(
        parent: Optional[QObject] = None,
        player_config_edit_view: Optional[Callable] = None,
    ):
        """Create the view that lists the players' game configurations.

        Parameters
        ----------
        parent : QObject | None, optional
            Parent of the view. Default is None.
        player_config_edit_view : Callable | None, optional
            Callable used to open the edit view. Default is None.

        Returns
        -------
        object
            The list view created by the game.
        """
        ...
