import subprocess
import platform
import os
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence  # Importar QShortcut e QKeySequence
from PySide6.QtCore import Qt, QObject
from udescjoinvilletteaview.selectplayerview import SelectPlayerView
from udescjoinvilletteaview.aboutview import AboutView    
from udescjoinvilletteacontroller.selectplayercontroller import SelectPlayerController
from udescjoinvilletteautil.pathconfig import PathConfig

class MenuHandler(QObject):  # Herdar de QObject
    """Classe para gerenciar ações do menu"""
    def __init__(self, parent):
        super().__init__(parent)  # Inicializar QObject com o parent
        self.parent = parent
        self.translator = parent.translator if hasattr(parent, "translator") else None
        self._is_exiting = False  # Flag para evitar chamadas duplicadas

        # Configurar atalho F1 para chamar show_help
        help_shortcut = QShortcut(QKeySequence(Qt.Key_F1), self.parent)
        help_shortcut.activated.connect(self.show_help)

    def do_nothing(self):
        """Ação placeholder para funcionalidades não implementadas"""
        dialog = QDialog(self.parent)  # Usa QDialog e passa o parent
        dialog.setWindowTitle("Placeholder")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(QPushButton("Do nothing button"))
        dialog.exec()  # Executa como modal

    def confirm_exit(self, event=None):
        """Confirmação de saída do sistema"""
        # Verifica se já está no processo de saída para evitar duplicação
        if self._is_exiting:
            if event is not None:
                event.accept()
            return

        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.parent.windowIcon())
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.parent.windowTitle())
        msg_box.setText(self.tr("Deseja sair do sistema?"))  # Usar self.tr
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # Traduzir os botões
        msg_box.button(QMessageBox.Yes).setText(self.tr("Sim"))  # Usar self.tr
        msg_box.button(QMessageBox.No).setText(self.tr("Não"))  # Usar self.tr

        response = msg_box.exec()
        
        if response == QMessageBox.Yes:
            self._is_exiting = True  # Define a flag para indicar que está saindo
            if event is not None:  # Se for um evento de fechamento da janela
                event.accept()
            else:  # Se for chamado pelo menu
                QApplication.quit()
        elif event is not None:  # Apenas ignorar se for evento de janela
            event.ignore()

    def call_selection(self):
        select = SelectPlayerView(self.parent)
        controller = SelectPlayerController(select, self.parent)
        
        controller.update_registers()

        select.exec()

    def show_help(self):
        """Abre o Qt Assistant com o arquivo de ajuda especificado."""
        help_file = "helppt.qhc"
        namespace = "ttea.qt.helppt/help"
        start_page = "index.html"

        # Caminho base para o PySide6
        pyside6_path = os.path.dirname(os.path.abspath(__import__("PySide6").__file__))
        assistant_name = "assistant.exe" if platform.system() == "Windows" else "assistant"
        assistant_path = os.path.join(pyside6_path, assistant_name)

        # Verifica se o assistant existe
        if not os.path.exists(assistant_path):
            raise FileNotFoundError(f"Qt Assistant não encontrado em: {assistant_path}")

        # Caminho do arquivo .qhc
        help_file_path = os.path.join(os.getcwd(), PathConfig.path_help_pt(help_file))

        if not os.path.exists(help_file_path):
            raise FileNotFoundError(f"Arquivo de ajuda não encontrado: {help_file_path}")

        # Comando para abrir o Qt Assistant com os argumentos
        command = [
            assistant_path,
            "-collectionFile", help_file_path,
            "-showUrl", f"qthelp://{namespace}/{start_page}"
        ]

        # Executa o comando
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def show_about(self):
        about = AboutView(self.parent)  # Passa o parent (janela principal)
        about.exec()  # Executa como modal