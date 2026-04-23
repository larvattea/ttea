from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QDialog

# Local module import
from udescjoinvilletteacontroller import PlayerGameLaunchController
from udescjoinvilletteamodel import AppModel, Language
from udescjoinvilletteaservice import PlayerGameLaunchService
from udescjoinvilletteaui import Ui_PlayerGameLaunchView
from udescjoinvilletteautil import MessageService, PathConfig
from udescjoinvilletteawindow import WindowConfig


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
        self.cbx_game.currentIndexChanged.connect(
            self.controller.update_tooltip
        )

        self.populate_comboboxes()

    def populate_comboboxes(self):
        # Players
        self.cbx_player.addItems(
            [p.name for p in self.service.get_all_players()]
        )

        # Professionals
        self.cbx_professional.addItems(
            [h.name for h in self.service.get_all_professionals()]
        )

        # 2. Popular Jogos com Metadados e Idioma
        language_app = AppModel.get_instance().current_language

        games = self.service.get_games_metadata()

        for g in games:
            # Busca a tradução dentro do dicionário 'language' do JSON
            trans = g.get("language", {}).get(
                language_app,
                g.get("language", {}).get(Language.DEFAULT_LANGUAGE, {}),
            )
            nome_exibicao = trans.get("name", g.get("game"))

            # Adiciona no combo e associa o dicionário completo ao item
            self.cbx_game.addItem(
                QIcon(PathConfig.icon_ui_menu(g.get("icon", ""))),
                nome_exibicao,
                g,
            )

            # Coloca o hint sobre o jogo
            index = self.cbx_game.count() - 1
            tooltip_text = trans.get("description")
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
        if self.msg.question(
            self.tr("Deseja sair da tela de sessão de jogo?"), None, True
        ):
            event.accept()
        else:
            event.ignore()
