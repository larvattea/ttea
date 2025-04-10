from PySide6.QtWidgets import QApplication, QStatusBar, QLabel, QMainWindow, QDialog
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from datetime import date

class WindowConfig:
    STAY_SIZE = 0
    INCREMENT_SIZE_PERCENT = 1
    DECREMENT_SIZE_PERCENT = 2

    """Classe para configurações fixas da janela do app exergame"""

    def _setup_window(self, title, icon, status=STAY_SIZE, width=0, height=0, parent=None):
        """Configura as propriedades da janela"""
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        
        # Calcula o tamanho base inicial
        base_width, base_height = self._get_base_size(parent)
        
        # Ajusta o tamanho conforme o status
        new_width = self._adjust_size(base_width, width, status)
        new_height = self._adjust_size(base_height, height, status)

        # Define o tamanho e centraliza
        self._center_window(parent, new_width, new_height)
        self.setFixedSize(new_width, new_height)

    def _get_base_size(self, parent):
        """Retorna o tamanho base com base na janela pai ou na tela"""
        if parent is not None and hasattr(parent, 'geometry'):
            parent_geo = parent.geometry()
            return parent_geo.width(), parent_geo.height()
        screen = QApplication.primaryScreen().geometry()
        return screen.width() // 2, screen.height() // 2

    def _adjust_size(self, base, percent, status):
        """Ajusta o tamanho base conforme o status e percentual"""
        if percent <= 0:
            return base
        if status == self.INCREMENT_SIZE_PERCENT:
            return base + (base * percent / 100)
        if status == self.DECREMENT_SIZE_PERCENT:
            return base - (base * percent / 100)
        return base

    def _center_window(self, parent=None, width=None, height=None):
        """Centraliza a janela em relação à janela pai ou na tela"""
        if width is None:
            width = self.width()
        if height is None:
            height = self.height()

        if parent is not None and hasattr(parent, 'geometry'):
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - width) // 2
            y = parent_geo.y() + (parent_geo.height() - height) // 2
        else:
            screen = QApplication.primaryScreen().geometry()
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