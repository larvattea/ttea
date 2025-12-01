import sys

import qtawesome as qta
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ActionButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Botões com Ícones Coloridos")
        self.setGeometry(100, 100, 500, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Linha 1: Salvar (verde), Editar (laranja), Excluir (vermelho)
        row1 = QHBoxLayout()
        salvar_icon = qta.icon("fa6s.floppy-disk", color="green")
        editar_icon = qta.icon("fa6s.pen-to-square", color="orange")
        excluir_icon = qta.icon("fa6s.trash", color="red")

        salvar_btn = QPushButton(salvar_icon, "Salvar")
        editar_btn = QPushButton(editar_icon, "Editar")
        excluir_btn = QPushButton(excluir_icon, "Excluir")

        row1.addWidget(salvar_btn)
        row1.addWidget(editar_btn)
        row1.addWidget(excluir_btn)
        layout.addLayout(row1)

        # Linha 2: Consultar (azul), OK (verde escuro), Cancelar (cinza)
        row2 = QHBoxLayout()
        consultar_icon = qta.icon("fa6s.magnifying-glass", color="blue")
        ok_icon = qta.icon("fa6s.check", color="#006400")  # Verde escuro
        cancelar_icon = qta.icon("fa6s.xmark", color="gray")

        consultar_btn = QPushButton(consultar_icon, "Consultar")
        ok_btn = QPushButton(ok_icon, "OK")
        cancelar_btn = QPushButton(cancelar_icon, "Cancelar")

        row2.addWidget(consultar_btn)
        row2.addWidget(ok_btn)
        row2.addWidget(cancelar_btn)
        layout.addLayout(row2)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActionButtons()
    window.show()
    sys.exit(app.exec())
