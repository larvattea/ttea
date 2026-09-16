from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from ttea.factory.gameviewfactoryprotocol import GameViewFactoryProtocol
from ttea.games.kartea.view import (PlayerKarteaConfigEditView,
                                    PlayerKarteaConfigListView)

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaConfig


class KarteaViewFactory(GameViewFactoryProtocol):

    @staticmethod
    def create_player_config_edit_view(
        parent: Optional[QDialog] = None,
        config: Optional["PlayerKarteaConfig"] = None,
    ) -> PlayerKarteaConfigEditView:
        return PlayerKarteaConfigEditView(parent, config)

    @staticmethod
    def create_player_config_list_view(
        parent: Optional[QObject] = None,
        player_config_edit_view: Optional[
            Callable[
                [Optional[QDialog], Optional["PlayerKarteaConfig"]],
                PlayerKarteaConfigEditView,
            ]
        ] = None,
    ) -> PlayerKarteaConfigListView:
        return PlayerKarteaConfigListView(parent, player_config_edit_view)
