from typing import Callable, Optional, Protocol

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog


class GameViewFactoryProtocol(Protocol):

    @staticmethod
    def create_player_config_edit_view(
        parent: Optional[QDialog] = None, config: Optional[object] = None
    ): ...

    @staticmethod
    def create_player_config_list_view(
        parent: Optional[QObject] = None,
        player_config_edit_view: Optional[Callable] = None,
    ): ...
