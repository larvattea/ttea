from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox
from udescjoinvilletteamodel.player import Player
from udescjoinvilletteaview.registerplayerview import RegisterPlayerView

class RegisterPlayerController(QObject):

    def __init__(self, view: RegisterPlayerView, parent=None):
        super().__init__(parent)
        self.view = view
        self.model = Player()


    def register_player(self):

        data = self.view.get_data()
        self.model.name = data["name"]
        self.model.birth_date = data["birth_date"]
        self.model.observations = data["observations"]

        if self.model.is_valid():
            print(f"Jogador cadastrado: {self.model}")
            self.view.clear_fields()
            self.view.accept()  # Fecha o diálogo com sucesso

        else:
            msg = QMessageBox()
            msg.setWindowIcon(self.view.windowIcon)
            msg.setWindowTitle("Aviso")
            msg.setIcon(QMessageBox.warning)
            msg.setText("Aviso: Nome e data de nascimento são obrigatórios.")
            msg.setParent(self.main_window)
            msg.exec()