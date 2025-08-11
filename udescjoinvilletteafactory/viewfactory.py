from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject, QTranslator
from PySide6.QtWidgets import QDialog

from udescjoinvilletteaview import (AboutView, LanguageView, PlayerEditView,
                                    PlayerListView)

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player


class ViewFactory:
    """Factory for creating view instances."""

    @staticmethod
    def create_player_edit_view(
        parent: Optional[QDialog] = None, player: Optional["Player"] = None
    ) -> PlayerEditView:
        """Create an instance of PlayerEditView."""
        return PlayerEditView(parent, player)

    @staticmethod
    def create_player_list_view(
        parent: Optional[QObject] = None,
        player_edit_view_factory: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], PlayerEditView]
        ] = None,
    ) -> PlayerListView:
        """Create an instance of PlayerListView."""
        return PlayerListView(parent, player_edit_view_factory)

    @staticmethod
    def create_about_view(parent: Optional[QObject] = None) -> AboutView:
        """Create an instance of AboutView."""
        return AboutView(parent)

    @staticmethod
    def create_language_view(
        translator: Optional[QTranslator] = None,
        parent: Optional[QObject] = None,
    ) -> LanguageView:
        """Create an instance of LanguageView."""
        return LanguageView(translator, parent)
