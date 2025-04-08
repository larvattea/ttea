from PySide6.QtWidgets import (
        QApplication, 
        QMainWindow, 
        QMenu, 
        QWidget, 
        QMenuBar, 
        QGridLayout, 
        QPushButton, 
        QFormLayout, 
        QLabel,
        QLineEdit,
        QDateEdit,
        QTextEdit, 
        QCalendarWidget)
from PySide6.QtGui import QAction
from sys import argv
from os import listdir


class RegisterPlayer(QWidget):
    
    def __init__(self, parent = None):
        super().__init__(parent)

        layout = QFormLayout(horizontalSpacing=-1)

        layout.addRow(QLabel("Nome: "), QLineEdit())
        layout.addRow(QLabel("Data de Nascimento:"), QCalendarWidget())
        layout.addRow(QLabel("Observações:"),QTextEdit())
        layout.addRow(QPushButton("Cadastrar"))


        self.setLayout(layout)

        self.setStyleSheet("""
            padding = 0px;    
        """)
        
        self.show()


#Horizontal Menu
# class NavBar(QMenuBar): 
        
#     def __init__(self, parent, games):
#         super().__init__(parent) 

#         player_menu = QMenu("Jogador", self)                
#         #player_menu actions 
#         register_action = QAction(text = "Cadastro", parent= player_menu)
#         exit_action = QAction (text = "Sair", parent= player_menu)

#         player_menu.addActions([register_action, exit_action])
    

#         games_menu  = QMenu("Jogos", self)
#         about_menu = QMenu("Menu", self )


#         #Add games' names dynamically to menu labels "Jogos" and "Sobre" 
#         for game in games:
#             game_action = QAction(text = game, parent = games_menu)
#             about_action = QAction(text = "Manual " + game, parent = about_menu)

#             games_menu.addAction(game_action)
#             about_menu.addAction(about_action)

    
#         settings_menu = QMenu("Configurações", self)

#         settings_menu_general = QAction("Conf. Gerais", settings_menu)
#         settings_menu_calibration = QAction("Calibração", settings_menu)

#         settings_menu.addActions([settings_menu_general, settings_menu_calibration])
        

#         about_menu.addSeparator()
#         about = QAction(text="Sobre", parent = about_menu)
#         about_menu.addAction(about)

#         self.addMenu(player_menu)
#         self.addMenu(games_menu)
#         self.addMenu(settings_menu)
#         self.addMenu(about_menu)



# class MainWindow(QMainWindow): 
#     def __init__(self):
#         super().__init__()

#         self.games = listdir(r".\Games")
#         self.setWindowTitle("T-TEA")

#         layout = QGridLayout()

#         self.register = Register(self)
#         self.menu = NavBar(self, self.games)

        
#         layout.setMenuBar(self.menu)
#         layout.addWidget(self.register)


#         layout.setMenuBar(self.menu)
#         widget = QWidget()
#         widget.setLayout(layout)

#         self.setCentralWidget(widget)
        




        