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
from datetime import datetime

class RegisterPlayerView(QDialog, WindowConfig):
    """Visão para o cadastro de jogador."""
    TITLE = "Cadastro de Jogador"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window(
            self.TITLE,                          # positional: title
            parent.windowIcon() if parent else None,  # positional: icon
            WindowConfig.DECREMENT_SIZE_PERCENT, # positional: status
            20,                                  # positional: width
            20,                                  # positional: height
            parent                               # positional: parent
        )
        # Widgets
        self.name_input = QLineEdit()
        self.birth_date_input = QCalendarWidget()
        self.observations_input = QTextEdit()
        self.register_button = QPushButton("Cadastrar")

        # Layout
        layout = QFormLayout()
        layout.addRow(QLabel("Nome:"), self.name_input)
        layout.addRow(QLabel("Data de Nascimento:"), self.birth_date_input)
        layout.addRow(QLabel("Observações:"), self.observations_input)
        layout.addRow(self.register_button)

        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        """Aplica estilos à interface."""
        self.setStyleSheet("""
            QFormLayout { margin: 10px; }
        """)

    def get_data(self) -> dict:
        """Retorna os dados inseridos pelo usuário."""
        return {
            "name": self.name_input.text(),
            "birth_date": self.birth_date_input.selectedDate().toPython(),
            "observations": self.observations_input.toPlainText()
        }

    def clear_fields(self):
        """Limpa os campos do formulário."""
        self.name_input.clear()
        self.birth_date_input.setSelectedDate(datetime.now())
        self.observations_input.clear()
   