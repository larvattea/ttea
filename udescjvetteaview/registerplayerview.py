from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import QDate
from udescjoinvilletteaapp.windowconfig import WindowConfig
from datetime import datetime

class RegisterPlayerView(QDialog, WindowConfig):
    """Visão para o cadastro de jogador."""
    TITLE = "Cadastro de Jogador"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window(
            self.TITLE,                          # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT, # status
            30,                                  # width
            30,                                  # height
            parent                               # parent
        )
        # Widgets
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome")  # Placeholder para orientação
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)  # Ativa o popup do calendário
        self.birth_date_input.setDate(QDate.currentDate())  # Define a data atual
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")  # Formato dd/mm/aaaa
        self.birth_date_input.setToolTip("Digite a data no formato dd/mm/aaaa ou use o calendário")  # Dica para formato
        self.birth_date_input.setSpecialValueText("")  # Evita texto padrão para data inválida
        self.observations_input = QTextEdit()
        self.observations_input.setPlaceholderText("Digite observações (opcional)")  # Placeholder
        self.register_button = QPushButton("Cadastrar")

        # Layout
        layout = QFormLayout()
        layout.addRow(QLabel("Nome:"), self.name_input)
        layout.addRow(QLabel("Data de Nascimento:"), self.birth_date_input)
        layout.addRow(QLabel("Observações:"), self.observations_input)
        layout.addRow(self.register_button)

        self.setLayout(layout)
        #self._apply_styles()

    def _apply_styles(self):
        """Aplica estilos à interface."""
        self.setStyleSheet("""
            QFormLayout {
                margin: 10px;
            }
            QDateEdit {
                padding: 4px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QDateEdit:focus {
                border-color: #0078d4;
            }
            QLineEdit, QTextEdit {
                padding: 4px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                padding: 6px;
                font-size: 14px;
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005ea2;
            }
            QCalendarWidget {
                background-color: #ffffff;
                font-size: 12px;
            }
        """)

    def get_data(self) -> dict:
        """Retorna os dados inseridos pelo usuário."""
        data = {
            "name": self.name_input.text().strip(),
            "birth_date": self.birth_date_input.date().toPython(),
            "observations": self.observations_input.toPlainText().strip()
        }
        if data["birth_date"] > datetime.now().date():
            raise ValueError("A data de nascimento não pode ser no futuro.")
        return data

    def clear_fields(self):
        """Limpa os campos do formulário."""
        self.name_input.clear()
        self.birth_date_input.setDate(QDate.currentDate())  # Reseta para a data atual
        self.observations_input.clear()

    def closeEvent(self, event):
        """Pergunta ao usuário se deseja fechar a janela."""
        # Verifica se há dados não salvos
        if (self.name_input.text().strip() or 
            self.observations_input.toPlainText().strip() or 
            self.birth_date_input.date() != QDate.currentDate()):
            # Cria uma instância de QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirmar Fechamento")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("Há dados não salvos. Deseja realmente fechar a janela?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            # Personaliza o texto dos botões, se desejar
            msg_box.button(QMessageBox.Yes).setText("Sim")
            msg_box.button(QMessageBox.No).setText("Não")
            # Executa a caixa de diálogo e verifica a resposta
            response = msg_box.exec()
            if response == QMessageBox.Yes:
                event.accept()  # Fecha a janela
            else:
                event.ignore()  # Cancela o fechamento
        else:
            #event.accept()  # Fecha a janela se não houver dados
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle(self.TITLE)
            msg_box.setText("Deseja sair do cadastro?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)

            # Traduzir os botões
            msg_box.button(QMessageBox.Yes).setText("Sim")
            msg_box.button(QMessageBox.No).setText("Não")

            response = msg_box.exec()
        
            if response == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()  # Cancela o fechamento
