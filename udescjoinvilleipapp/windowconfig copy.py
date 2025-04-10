from PySide6.QtWidgets import QApplication, QStatusBar, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from datetime import date

class WindowConfig():
    STAY_SIZE = 0
    INCREMENT_SIZE_PERCENT = 1
    DECREMENT_SIZE_PERCENT = 2

    """Classe para configurações fixas da janela do app exergame"""

    def _setup_window(self, title, icon, width=0, height=0, parent=None):
        """Configura as propriedades da janela"""
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self._center_window(parent)  # Passa o parent como parâmetro
        if width > 0 and height > 0:
            self.setFixedSize(self.width() - ((self.width()*width)/100), 
                            self.height() - ((self.height()*height)/100))
        elif width > 0:
            self.setFixedSize(self.width() - ((self.width()*width)/100), 
                            self.height())
        elif height > 0:
            self.setFixedSize(self.width(), 
                            self.height() - ((self.height()*height)/100))
        else:
            self.setFixedSize(self.width(), self.height())

    def _center_window(self, parent=None):
        """Centraliza a janela em relação à janela pai ou na tela se não houver parent"""
        if parent is not None and hasattr(parent, 'geometry'):
            # Centraliza em relação à janela pai
            parent_geo = parent.geometry()
            width = self.width()
            height = self.height()
            x = parent_geo.x() + (parent_geo.width() - width) // 2
            y = parent_geo.y() + (parent_geo.height() - height) // 2
            self.setGeometry(x, y, width, height)
        else:
            # Centraliza na tela (comportamento original)
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