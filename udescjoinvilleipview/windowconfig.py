from PySide6.QtWidgets import QApplication, QStatusBar, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from datetime import date

class WindowConfig():
    """Classe para configurações fixas da janela do app exergame"""

    def _setup_window(self, title, icon):
        """Configura as propriedades da janela"""
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self._center_window()
        self.setFixedSize(self.width(), self.height())

    def _center_window(self):
        """Centraliza a janela na tela"""
        screen = QApplication.primaryScreen().geometry()
        width = screen.width() // 2
        height = screen.height() // 2
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)
    
    def _setup_status_bar(self, version):
        """Configura a barra de status"""
        today = date.today().strftime("%d/%m/%Y")
        status_text = f"Versão da Plataforma: {version} - Data Atual: {today}"
        status_bar_label = QLabel(status_text)
        status_bar_label.setAlignment(Qt.AlignRight)
        status_bar_label.setStyleSheet("border: 1px sunken; padding: 2px;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(status_bar_label)
        self.setStatusBar(status_bar)    