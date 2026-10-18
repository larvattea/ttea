from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QDialog

# Local module import
from ttea.controller import PlayerGameLaunchController
from ttea.model import AppModel
from ttea.service import PlayerGameLaunchService
from ttea.ui import Ui_PlayerGameLaunchView
from ttea.util import MessageService
from ttea.window import WindowConfig


class PlayerGameLaunchView(QDialog, Ui_PlayerGameLaunchView, WindowConfig):

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

        # Initialize controller
        self.controller = PlayerGameLaunchController(self)
        self.pb_cancel.clicked.connect(self.controller.handle_cancel)
        self.pb_play.clicked.connect(self.controller.launch_game)
        self.pb_game_info.clicked.connect(self.controller.handle_game_info)
        self.cbx_game.currentIndexChanged.connect(
            self.controller.update_tooltip
        )
        # Analisando sinal finished (o QDialog emite um int)
        # abordagem diferente
        self.finished.connect(lambda result: self.controller.cleanup())

        self.populate_comboboxes()

    def populate_comboboxes(self):
        # Players
        for p in self.service.get_all_players():
            self.cbx_player.addItem(p.name, p.id)

        # Professionals
        for h in self.service.get_all_professionals():
            self.cbx_professional.addItem(h.name, h.id)

        # Jogos com metadados e tradução
        language_app = AppModel.get_instance().current_language

        games = self.service.get_games_metadata()

        for g in games:
            # Adiciona no combo e associa o GameMetadata ao item
            self.cbx_game.addItem(
                QIcon(g.icon_path),
                g.name(language_app),
                g,
            )

            # Coloca o hint sobre o jogo
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
        """Override close event to confirm exit.

        Shows a confirmation dialog before allowing the window to close.

        Parameters
        ----------
        event : QCloseEvent
            The close event to accept or ignore.
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
