from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QCalendarWidget,
    QTextEdit,
    QPushButton,
)
from udescjoinvilleipapp.windowconfig import WindowConfig

class RegisterPlayer(QDialog, WindowConfig):
    TITLE = "Cadastro de Jogador"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window(self.TITLE, parent.windowIcon())  # Passa o ícone da janela pai

        layout = QFormLayout()
        layout.addRow(QLabel("Nome:"), QLineEdit())
        layout.addRow(QLabel("Data de Nascimento:"), QCalendarWidget())
        layout.addRow(QLabel("Observações:"), QTextEdit())
        layout.addRow(QPushButton("Cadastrar"))

        self.setLayout(layout)

        self.setStyleSheet("""
            QFormLayout { margin: 10px; }
        """)
