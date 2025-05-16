from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMainWindow, QStatusBar, QMenu, QMenuBar, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QCoreApplication

from datetime import date

from udescjoinvilletteaapp.windowconfig import WindowConfig
from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteaapp.menuhandler import MenuHandler

class TTeaApp(QMainWindow, WindowConfig):
    ICON_APP = PathConfig.icon("larva.ico")
    LOGO_APP = PathConfig.image("ttealogo.png")
    VERSION = "2.0"
    PLATAFORM_SUFIX = "TEA"
    PLATAFORM_MANUAL = "Manual"

    @staticmethod
    def get_title():
        return QCoreApplication.translate("TTeaApp", "Plataforma T-TEA")

    def __init__(self, translator = None, app = None):
        super().__init__()
        self.translator = translator  # Objeto tradutor do main.py
        self.app = app
        self.menu_handler = MenuHandler(self)
        self.settings = QSettings(PathConfig.inifile("config.ini"), QSettings.IniFormat)
        self._setup_window(TTeaApp.get_title(), self.ICON_APP)
        self._setup_menu()
        self._setup_status_bar(self.VERSION)
    
        
    def _setup_menu(self):
        """Configura o menu principal"""
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        paths = PathConfig.path_games()
        games = []
        helps = []

        for path in paths:
            path = (path.replace(self.PLATAFORM_SUFIX.lower(), self.PLATAFORM_SUFIX) 
                    if self.PLATAFORM_SUFIX.lower() in path 
                    else path)
            if path:
                path = path[0].upper() + path[1:]
            # Mapeamento de ícones por jogo
            game_icons = {
                "kartea": PathConfig.icon("kartea4.ico") 
                # Adicione outros jogos aqui
            }
            # Usa ícone específico ou genérico como fallback
            icon_path = game_icons.get(path.lower(), PathConfig.image("kartea.png"))
            games.append((path, self.menu_handler.do_nothing, icon_path))
            helps.append((self.PLATAFORM_MANUAL+" "+ path, self.menu_handler.do_nothing))  

        menu_configs = [
            (self.tr("&Cadastro"), [(self.tr("&Jogador"), self.menu_handler.call_selection),
                         (self.tr("&Sair"), self.menu_handler.confirm_exit)]),
            (self.tr("&Exergames"), games),             
            (self.tr("C&onfigurações"), games + [(self.tr("&Calibração"), self.menu_handler.do_nothing)]),
            (self.tr("&Ajuda"), helps +
                      [(self.tr("&Sobre..."), self.menu_handler.show_about)]),
        ]

        for menu_name, items in menu_configs:
            menu = QMenu(menu_name, self)
            self._populate_menu(menu, items)
            menubar.addMenu(menu)

    def _populate_menu(self, menu, items):
        """Preenche um menu com itens """
        for item in items:
            label, action = item[0], item[1]
            # Verifica se deve adicionar separador
            if label in [self.tr("&Sair"), self.tr("&Calibração"), self.tr("&Sobre...")]:
                menu.addSeparator()
            # Cria a ação do menu
            menu_action = menu.addAction(label, action)
            # Adiciona ícone se houver (para itens de games)
            if len(item) > 2 and item[2]:  # Verifica se há um terceiro elemento (icon_path)
                menu_action.setIcon(QIcon(item[2]))
    
    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento da janela"""
        self.menu_handler.confirm_exit(event)     

    def _setup_status_bar(self, version):
        """Configura a barra de status"""
        mask = self.settings.value(self.app.GENERAL_DATE_MASK, None)
        status_text = ("{} {} - {} {}").format(
        self.tr("Versão da Plataforma:"), version, self.tr("Data Atual:"), date.today().strftime(mask))
        status_bar_label = QLabel(status_text)
        status_bar_label.setAlignment(Qt.AlignRight)
        status_bar_label.setStyleSheet("border: 1px sunken; padding: 2px;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(status_bar_label)
        self.setStatusBar(status_bar)           