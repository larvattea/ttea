# udescjoinvilletteaview/mainview.py
from datetime import date
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar, QWidget

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteacontroller import MainController
from udescjoinvilletteamodel import AppModel
from udescjoinvilletteaui import Ui_MainView
from udescjoinvilletteautil import MessageService
from udescjoinvilletteawindow import WindowConfig


class MainView(QMainWindow, Ui_MainView, WindowConfig):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):

        super().__init__(parent)
        self.setupUi(self)

        self.setup_window(
            AppConfig.get_title(),
            None,
            WindowConfig.DECREMENT_SIZE_PERCENT,
            5,
            5,
            parent,
        )

        self.controller = MainController(
            self, AppModel.get_instance(), MessageService(self)
        )

        # === CONEXÕES DIRETAS DOS WIDGETS/ACTIONS AO CONTROLLER ===
        self.act_exit.triggered.connect(self.controller.handle_exit)
        self.act_player.triggered.connect(self.controller.open_player_list)
        self.act_kartea.triggered.connect(
            self.controller.open_kartea_player_config
        )
        self.act_calibration.triggered.connect(
            self.controller.open_calibration
        )
        self.act_help.triggered.connect(self.controller.open_help)
        self.act_about.triggered.connect(self.controller.open_about)

        # Menu dinâmico de jogos (preenchido pelo controller depois)
        self.mnu_exergames.triggered.connect(self.controller.start_game)

        self.msg = MessageService(self)
        self._setup_status_bar()

    def _setup_status_bar(self):
        """Cria o QLabel com versão e data e adiciona permanentemente na status bar"""
        date_mask = AppConfig.get_geral_date_mask() or "%d/%m/%Y"

        version = self.tr("Versão da plataforma: {0}")
        version = version.format(AppConfig.VERSION)

        current_date = self.tr("Data atual: {0}")
        current_date = current_date.format(date.today().strftime(date_mask))

        status_text = version + " - " + current_date

        status_bar_label = QLabel(status_text)
        status_bar_label.setAlignment(Qt.AlignRight)
        status_bar_label.setStyleSheet("border: 1px sunken; padding: 2px;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(status_bar_label)
        self.setStatusBar(status_bar)

    def populate_games_menu(self, games: list[tuple[str, str]]):
        """Chamado pelo controller para preencher menu (já ordenado)"""
        self.mnu_exergames.clear()
        if not games:
            self.mnu_exergames.setTitle(
                self.tr("Exergames (nenhum encontrado)")
            )
            self.mnu_exergames.setEnabled(False)
            return
        for display_name, icon_path in games:
            action = self.mnu_exergames.addAction(display_name)
            if icon_path:
                action.setIcon(QIcon(icon_path))
            action.setData(
                display_name
            )  # Controller pega via start_game(action.data())

    def update_status_message(self, message: str, timeout: int = 6000):
        self.statusBar().showMessage(message, timeout)

    def show_critical_error(self, title: str, text: str):
        self.msg.critical(text, title)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.controller.try_close():
            event.accept()
        else:
            event.ignore()
