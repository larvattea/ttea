import sys

import qtawesome as qta
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


def main():
    app = QApplication(sys.argv)

    # Janela principal
    window = QWidget()
    layout = QVBoxLayout(window)

    # Função auxiliar para criar QIcon padrão compatível
    def qta_to_qicon(icon_name, color):
        qa_icon = qta.icon(icon_name, color=color)
        pix = qa_icon.pixmap(19, 19)  # Gera QPixmap no tamanho desejado
        return QIcon(pix)

    # Exemplo de ícones Font Awesome 6
    # 1. Cria o QPushButton
    btn_save = QPushButton("Salvar")
    # 2. Define o ícone no QPushButton
    btn_save.setIcon(qta_to_qicon("fa6s.plus", "blue"))

    # Salvando ícones como PNG (Mantém o objeto QIcon em uma variável temporária ou separado)
    plus_icon_for_save = qta.icon("fa6s.plus", color="blue")
    plus_icon_for_save.pixmap(19, 19).save("fa6s_plus.png", "PNG")

    # 1. Cria o QPushButton
    btn_open = QPushButton("Abrir")
    # 2. Define o ícone no QPushButton
    btn_open.setIcon(qta_to_qicon("fa6s.pen-to-square", "black"))

    open_icon_for_save = qta.icon("fa6s.pen-to-square", color="black")
    open_icon_for_save.pixmap(19, 19).save("fa6s_pen_to_square.png", "PNG")

    # 1. Cria o QPushButton
    btn_delete = QPushButton("Excluir")
    # 2. Define o ícone no QPushButton
    btn_delete.setIcon(qta_to_qicon("fa6s.trash", "red"))

    delete_icon_for_save = qta.icon("fa6s.trash", color="red")
    delete_icon_for_save.pixmap(19, 19).save("fa6s_trash.png", "PNG")

    # Adiciona os botões (QWidget) ao layout
    # Use btn_save em vez de plus_icon original
    layout.addWidget(btn_save)
    layout.addWidget(btn_open)
    layout.addWidget(btn_delete)

    window.setWindowTitle("Exemplo PySide6 + QtAwesome 6")
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
