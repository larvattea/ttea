"""Game launch (game session) dialog."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QDialog

from ttea.controller import PlayerGameLaunchController
from ttea.model import AppModel
from ttea.service import PlayerGameLaunchService
from ttea.ui import Ui_PlayerGameLaunchView
from ttea.util import MessageService
from ttea.window import WindowConfig


class PlayerGameLaunchView(QDialog, Ui_PlayerGameLaunchView, WindowConfig):
    """Dialog to choose a player, a professional and a game, and play.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent widget. Default is None.

    Attributes
    ----------
    msg : MessageService
        Service used to show dialogs.
    service : PlayerGameLaunchService
        Source of players, professionals and games.
    controller : PlayerGameLaunchController
        Controller of the dialog.

    Notes
    -----
    The window is fixed at 30% narrower and 10% shorter than the parent.
    When the dialog finishes, ``controller.cleanup`` stops a running
    game.
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
    ) -> None:

        super().__init__(parent)
        self.setupUi(self)
        self.msg = MessageService(self)

        self.setup_window(
            None,
            None,
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            30,  # width
            10,  # height
            parent,  # parent
        )
        self.service = PlayerGameLaunchService()

        self.controller = PlayerGameLaunchController(self)
        self.pb_cancel.clicked.connect(self.controller.handle_cancel)
        self.pb_play.clicked.connect(self.controller.launch_game)
        self.pb_game_info.clicked.connect(self.controller.handle_game_info)
        self.cbx_game.currentIndexChanged.connect(
            self.controller.update_tooltip
        )
        # Clean up on the finished(int) signal (the result is ignored)
        # instead of in closeEvent.
        self.finished.connect(lambda result: self.controller.cleanup())

        self.populate_comboboxes()

    def populate_comboboxes(self):
        """Fill the player, professional and game combo boxes.

        Notes
        -----
        Players and professionals are sorted by name, with their IDs as
        item data. Each game shows its icon and localized name, keeps
        its ``GameMetadata`` as item data and has its localized short
        description as tooltip.
        """
        # Players
        for p in self.service.get_all_players():
            self.cbx_player.addItem(p.name, p.id)

        # Professionals
        for h in self.service.get_all_professionals():
            self.cbx_professional.addItem(h.name, h.id)

        # Games, with localized names
        language_app = AppModel.get_instance().current_language

        games = self.service.get_games_metadata()

        for g in games:
            self.cbx_game.addItem(
                QIcon(g.icon_path),
                g.name(language_app),
                g,
            )

            # Tooltip with the short description
            index = self.cbx_game.count() - 1
            tooltip_text = g.text(language_app, "short_description")
            self.cbx_game.setItemData(
                index, tooltip_text, Qt.ItemDataRole.ToolTipRole
            )

        if self.cbx_game.count() > 0:
            first_tooltip = self.cbx_game.itemData(
                0, Qt.ItemDataRole.ToolTipRole
            )
            self.cbx_game.setToolTip(first_tooltip)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask for confirmation before closing.

        Parameters
        ----------
        event : QCloseEvent
            Close event.

        Notes
        -----
        If a game is running, the user is warned that it will be closed;
        confirming rejects the dialog (which stops the game through
        ``cleanup``).
        """
        if self.controller.is_game_running():
            if self.msg.question(
                self.tr(
                    "Há um jogo em execução e ele será encerrado. Deseja sair da tela de sessão de jogo?"
                ),
                None,
                True,
            ):
                self.reject()
            else:
                event.ignore()
        else:
            if self.msg.question(
                self.tr("Deseja sair da tela de sessão de jogo?"), None, True
            ):
                event.accept()
            else:
                event.ignore()
