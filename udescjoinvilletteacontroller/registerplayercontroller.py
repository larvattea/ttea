from PySide6.QtCore import QObject
from udescjoinvilletteautil.cvshandler import CSVHandler
from PySide6.QtWidgets import QMessageBox
from udescjoinvilletteamodel.player import Player
from udescjoinvilletteautil.pathconfig import PathConfig
from udescjoinvilletteaview.registerplayerview import RegisterPlayerView

class RegisterPlayerController(QObject):

    def __init__(self, view: RegisterPlayerView, parent=None):
        super().__init__(parent)
        self.view = view
        self.model = Player()


        self.view.register_button.clicked.connect(self.register_player)

    def register_player(self):
        
        main_csv = CSVHandler() 
        data = self.view.get_data()
        self.model.name = data["name"]
        self.model.birth_date = data["birth_date"]
        self.model.observations = data["observations"]


        if self.model.is_valid():

            self.model.player_identifier = main_csv.get_last_serial(PathConfig.players_dir)
            self.view.clear_fields()
            main_csv.write_csv(self.model.update_file(), [data])
            self.view.accept()  # Fecha o diálogo com sucesso
            print("jogador_cadastrado")
        else:
            msg = QMessageBox()
            msg.setWindowIcon(self.view.windowIcon())
            msg.setWindowTitle("Aviso")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Aviso: Nome e data de nascimento são obrigatórios.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()