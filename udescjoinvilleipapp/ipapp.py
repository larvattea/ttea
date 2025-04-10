from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QMenu, QMenuBar
from udescjoinvilleipapp.windowconfig import WindowConfig
from udescjoinvilleiputil.pathconfig import PathConfig
from udescjoinvilleipapp.menuhandler import MenuHandler

class IPApp(QMainWindow, WindowConfig):
    TITLE = "Plataforma IPlane"
    ICON_PATH = PathConfig.icon("larva.ico")
    LOGO_PATH = PathConfig.image("ttealogo.png")
    VERSION = "2.0"
    PLATAFORM_SUFIX = "TEA"
    PLATAFORM_MANUAL = "Manual"

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

        paths = PathConfig.path_games()
        games = []
        helps = []

        for path in paths:
            path = (path.replace(self.PLATAFORM_SUFIX.lower(), self.PLATAFORM_SUFIX) 
            if self.PLATAFORM_SUFIX.lower() in path 
            else path)
            if path:
                path = path[0].upper() + path[1:]
            games.append((path, self.menu_handler.do_nothing))
            helps.append((self.PLATAFORM_MANUAL+" "+ path, self.menu_handler.do_nothing))  

        menu_configs = [
            ("&Cadastro", [("&Jogador", self.menu_handler.call_register),
                         ("&Sair", self.menu_handler.confirm_exit)]),
            ("&Exergames", games),             
            ("C&onfigurações", games + [("&Calibração", self.menu_handler.do_nothing)]),
            ("&Ajuda", helps +
                      [("&Sobre...", self.menu_handler.show_about)]),
        ]

        for menu_name, items in menu_configs:
            menu = QMenu(menu_name, self)
            self._populate_menu(menu, items)
            menubar.addMenu(menu)

    def _populate_menu(self, menu, items):
        """Preenche um menu com itens (Princípio DRY)"""
        for label, action in items:
            if label == "&Sair" or label == "&Calibração" or label == "&Sobre...":
                menu.addSeparator()
            menu.addAction(label, action)
    
    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento da janela"""
        self.menu_handler.confirm_exit(event)            