from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QMenu, QMenuBar
from PySide6.QtGui import QIcon
from udescjoinvilletteaapp.windowconfig import WindowConfig
from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteaapp.menuhandler import MenuHandler

class IPApp(QMainWindow, WindowConfig):
    TITLE = "Plataforma T-TEA"
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
            ("&Cadastro", [("&Jogador", self.menu_handler.call_selection),
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
        for item in items:
            label, action = item[0], item[1]
            # Verifica se deve adicionar separador
            if label in ["&Sair", "&Calibração", "&Sobre..."]:
                menu.addSeparator()
            # Cria a ação do menu
            menu_action = menu.addAction(label, action)
            # Adiciona ícone se houver (para itens de games)
            if len(item) > 2 and item[2]:  # Verifica se há um terceiro elemento (icon_path)
                menu_action.setIcon(QIcon(item[2]))
    
    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento da janela"""
        self.menu_handler.confirm_exit(event)            