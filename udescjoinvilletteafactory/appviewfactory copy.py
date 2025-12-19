from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject, QTranslator
from PySide6.QtWidgets import QDialog

from udescjoinvilletteaview import (AboutView, LanguageView, PlayerEditView,
                                    PlayerListView)

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player


class AppViewFactory:
    """A factory class for creating application view instances.
    This class provides static methods to instantiate various view classes
    used in the application, such as PlayerEditView, PlayerListView,
    AboutView, and LanguageView. It facilitates the creation of view
    objects with optional parameters for parent widgets and other
    dependencies.

    Methods
    -------
    create_player_edit_view(parent=None, player=None)
        Create an instance of PlayerEditView.
    create_player_list_view(parent=None, player_edit_view=None)
        Create an instance of PlayerListView.
    create_about_view(parent=None)
        Create an instance of AboutView.
    create_language_view(translator=None, parent=None)
        Create an instance of LanguageView.

    """

    @staticmethod
    def create_player_edit_view(
        parent: Optional[QDialog] = None, player: Optional["Player"] = None
    ) -> PlayerEditView:
        """
        Create an instance of PlayerEditView.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            The parent dialog for the PlayerEditView, by default None.
        player : Optional[Player], optional
            The player object to be edited, by default None.

        Returns
        -------
        PlayerEditView
            An instance of PlayerEditView configured with the provided
            parent and player.
        """
        return PlayerEditView(parent, player)

    @staticmethod
    def create_player_list_view(
        parent: Optional[QObject] = None,
        player_edit_view: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], PlayerEditView]
        ] = None,
    ) -> PlayerListView:
        """
        Create an instance of PlayerListView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the PlayerListView, by default None.
        player_edit_view : Optional[Callable], optional
            A callable to create a PlayerEditView instance, by default
            None.

        Returns
        -------
        PlayerListView
            An instance of PlayerListView configured with the provided
            parent and player_edit_view callable.
        """
        return PlayerListView(parent, player_edit_view)

    @staticmethod
    def create_about_view(parent: Optional[QObject] = None) -> AboutView:
        """
        Create an instance of AboutView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the AboutView, by default None.

        Returns
        -------
        AboutView
            An instance of AboutView configured with the provided parent.
        """
        return AboutView(parent)

    @staticmethod
    def create_language_view(
        translator: Optional[QTranslator] = None,
        parent: Optional[QObject] = None,
    ) -> LanguageView:
        """
        Create an instance of LanguageView.

        Parameters
        ----------
        translator : Optional[QTranslator], optional
            The translator object for handling language settings, by
            default None.
        parent : Optional[QObject], optional
            The parent object for the LanguageView, by default None.

        Returns
        -------
        LanguageView
            An instance of LanguageView configured with the provided
            translator and parent.
        """
        return LanguageView(translator, parent)
