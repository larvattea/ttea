from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from udescjoinvilletteacontroller import PlayerListController
from udescjoinvilletteagames.kartea.controller import \
    PlayerKarteaConfigEditController
from udescjoinvilletteagames.kartea.view import (PlayerKarteaConfigEditView,
                                                 PlayerKarteaConfigListView)

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig


class KarteaViewFactory:
    """Factory for creating Kartea-related view instances.

    This class provides static methods to instantiate views for editing
    and listing Kartea game player configurations. It ensures that views
    are properly initialized with their controllers and optional parent
    objects.

    Attributes
    ----------
    None

    Methods
    -------
    create_player_kartea_config_edit_view(parent=None, config=None)
        Create an instance of PlayerKarteaConfigEditView with its controller.
    create_player_kartea_config_list_view(parent=None,
        player_kartea_config_edit_view_factory=None) Create an
        instance of PlayerKarteaConfigListView.
    """

    @staticmethod
    def create_player_kartea_config_edit_view(
        parent: Optional[QDialog] = None,
        config: Optional["PlayerKarteaConfig"] = None,
    ) -> PlayerKarteaConfigEditView:
        """Create an instance of PlayerKarteaConfigEditView with
        its controller.

        Initializes a PlayerKarteaConfigEditView with a corresponding
        controller, linking it to a PlayerListController for player data
        access. The controller's view reference is updated after creation.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            The parent dialog for the view. Defaults to None.
        config : Optional[PlayerKarteaConfig], optional
            The configuration to edit, if any. Defaults to None.

        Returns
        -------
        PlayerKarteaConfigEditView
            The initialized view with its controller.
        """
        player_list_controller = PlayerListController(None, None)
        # Create controller first with temporary None view
        controller = PlayerKarteaConfigEditController(
            None, config, player_list_controller
        )
        # Create view with the controller
        view = PlayerKarteaConfigEditView(parent, config, controller)
        # Update controller's view reference
        controller.set_view(view)
        return view

    @staticmethod
    def create_player_kartea_config_list_view(
        parent: Optional[QObject] = None,
        player_kartea_config_edit_view_factory: Optional[
            Callable[
                [Optional[QDialog], Optional["PlayerKarteaConfig"]],
                PlayerKarteaConfigEditView,
            ]
        ] = None,
    ) -> PlayerKarteaConfigListView:
        """Create an instance of PlayerKarteaConfigListView.

        Initializes a PlayerKarteaConfigListView with an optional factory
        function for creating edit views. If no factory is provided, it
        defaults to create_player_kartea_config_edit_view.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the view. Defaults to None.
        player_kartea_config_edit_view_factory : Optional[Callable], optional
            Factory function to create PlayerKarteaConfigEditView instances.
            Defaults to create_player_kartea_config_edit_view if None.

        Returns
        -------
        PlayerKarteaConfigListView
            The initialized view.
        """
        if player_kartea_config_edit_view_factory is None:
            player_kartea_config_edit_view_factory = (
                KarteaViewFactory.create_player_kartea_config_edit_view
            )
        return PlayerKarteaConfigListView(
            parent, player_kartea_config_edit_view_factory
        )
