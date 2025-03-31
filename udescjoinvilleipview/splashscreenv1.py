from PySide6.QtWidgets import QSplashScreen, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from udescjoinvilleiputil.pathconfig import PathConfig
from udescjoinvilleipapp.ipapp import IPApp

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Carrega a imagem do splash
        pixmap = QPixmap(PathConfig.image("ttealogo.png"))
        super().__init__(pixmap)
        
        # Configurações básicas da splash screen
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # Cria e configura a barra de progresso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(
            pixmap.width() // 4,  # Centraliza horizontalmente
            pixmap.height() - 50, # Posiciona abaixo da imagem
            pixmap.width() // 2,  # Largura proporcional à imagem
            20                    # Altura fixa
        )
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        
        # Configura o timer para simular o progresso
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # Atualiza a cada 50ms

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        
        if self.progress >= 100:
            self.timer.stop()
            self.close()
            self.main_window = IPApp()
            self.main_window.show()
