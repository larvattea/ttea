# udescjoinvilletteaview/mainview.py
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteaui import Ui_MainView
from udescjoinvilletteautil import MessageService
from udescjoinvilletteawindow import WindowConfig


class MainView(QMainWindow, Ui_MainView, WindowConfig):
    # Sinais que o Controller vai escutar
    exit_requested = Signal()
    player_list_requested = Signal()
    player_kartea_config_requested = Signal()
    calibration_requested = Signal()
    help_requested = Signal()
    about_requested = Signal()
    game_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainView()
        self.ui.setupUi(self)

        # Configurações básicas da janela
        self.setWindowTitle(AppConfig.get_title())
        self.setWindowIcon(QIcon(AppConfig.ICON_APP))

        # Status bar com versão + data atual
        self._setup_status_bar()

        # Conexões diretas dos menus (ações já existem no .ui)
        self.ui.actionSair.triggered.connect(self.exit_requested.emit)
        self.ui.actionGerenciar_Jogadores.triggered.connect(
            self.player_list_requested.emit
        )
        self.ui.actionConfiguracao_KarTEA.triggered.connect(
            self.player_kartea_config_requested.emit
        )
        self.ui.actionCalibracao.triggered.connect(
            self.calibration_requested.emit
        )
        self.ui.actionAjuda.triggered.connect(self.help_requested.emit)
        self.ui.actionSobre.triggered.connect(self.about_requested.emit)

        # Menu de jogos será preenchido dinamicamente pelo Controller
        self.ui.menu_Exergames.triggered.connect(
            self._on_game_action_triggered
        )
        self.msg = MessageService(self)

    def _setup_status_bar(self):
        """Cria o QLabel com versão e data e adiciona permanentemente na status bar"""
        date_mask = AppConfig.get_geral_date_mask() or "%d/%m/%Y"
        status_text = (
            f"{self.tr('Versão da Plataforma:')} {AppConfig.VERSION}  •  "
            f"{self.tr('Data Atual:')} {date.today().strftime(date_mask)}"
        )

        label = QLabel(status_text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet(
            """
            QLabel {
                padding: 4px 8px;
                background: palette(midlight);
                border: 1px solid palette(mid);
                border-radius: 4px;
                font-size: 10pt;
            }
        """
        )

        # Adiciona como widget permanente (fica à direita)
        self.statusBar().addPermanentWidget(label)

    def populate_games_menu(self, games: list[tuple[str, str]]):
        """Preenche o menu Exergames – agora recebe lista já ordenada"""
        self.ui.menu_Exergames.clear()

        if not games:
            self.ui.menu_Exergames.setTitle(
                self.tr("Exergames (nenhum encontrado)")
            )
            self.ui.menu_Exergames.setEnabled(False)
            return

        # Não ordena mais aqui → Controller já fez
        for display_name, icon_path in games:
            action = self.ui.menu_Exergames.addAction(display_name)
            if icon_path:
                action.setIcon(QIcon(icon_path))
            action.setData(display_name)

    def _on_game_action_triggered(self, action):
        """Captura clique em qualquer jogo do menu Exergames"""
        game_name = action.data()
        if game_name:
            self.game_selected.emit(game_name)

    def update_status_message(self, message: str, timeout: int = 6000):
        """Mostra mensagem temporária na status bar"""
        self.statusBar().showMessage(message, timeout)

    def show_critical_error(self, title: str, text: str):
        """Exibe erro crítico usando o serviço centralizado"""
        self.msg.critical(text, title)
