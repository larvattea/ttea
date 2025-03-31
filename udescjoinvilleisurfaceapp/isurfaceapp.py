from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QMenu, QMenuBar
from udescjoinvilleisurfaceview.windowconfig import WindowConfig
from udescjoinvilleisurfaceutil.pathconfig import PathConfig
from udescjoinvilleisurfaceapp.menuhandler import MenuHandler

class ISurfaceApp(QMainWindow, WindowConfig):
    TITLE = "Plataforma ISurface"
    ICON_PATH = PathConfig.icon("larva.ico")
    LOGO_PATH = PathConfig.image("ttealogo.png")
    VERSION = "2.0"

    def __init__(self):
        super().__init__()
        self.menu_handler = MenuHandler(self)
        self._setup_window(self.TITLE, self.ICON_PATH)
        self._setup_menu()
        self._setup_status_bar(self.VERSION)
    
    def _setup_menu(self):
        """Configura o menu principal"""
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        menu_configs = [
            ("Cadastro", [("Jogador", self.menu_handler.do_nothing),
                         ("Sair", self.menu_handler.confirm_exit)]),
            ("Exergames", [("KarTEA", self.menu_handler.do_nothing),
                          ("RepeTEA", self.menu_handler.do_nothing),
                          ("VesTEA", self.menu_handler.do_nothing)]),
            ("Configurações", [("KarTEA", self.menu_handler.do_nothing),
                              ("RepeTEA", self.menu_handler.do_nothing),
                              ("VesTEA", self.menu_handler.do_nothing),
                              ("Calibração", self.menu_handler.do_nothing)]),
            ("Ajuda", [("Manual KarTEA", self.menu_handler.do_nothing),
                      ("Manual RepeTEA", self.menu_handler.do_nothing),
                      ("Manual VesTEA", self.menu_handler.do_nothing),
                      ("Sobre...", self.menu_handler.show_about)])
        ]

        for menu_name, items in menu_configs:
            menu = QMenu(menu_name, self)
            self._populate_menu(menu, items)
            menubar.addMenu(menu)

    def _populate_menu(self, menu, items):
        """Preenche um menu com itens (Princípio DRY)"""
        for label, action in items:
            if label == "Sair" or label == "Sobre...":
                menu.addSeparator()
            menu.addAction(label, action)
    
    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento da janela"""
        self.menu_handler.confirm_exit(event)            