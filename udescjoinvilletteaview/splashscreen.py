from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QPixmap
from udescjoinvilletteautil.pathconfig import PathConfig

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(PathConfig.image("ttealogo.png"))
        super().__init__(pixmap)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.status_label = QLabel("Iniciando...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            background: rgba(0, 0, 0, 150);
            padding: 5px;
        """)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ffffff;
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 200);
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc00, stop:1 #006600);
                border-radius: 3px;
            }
        """)
        
        self.update_layout()
        
        self.animation = QPropertyAnimation(self.progress_bar, b"value")
        self.animation.setDuration(3000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(750)
        
        self.animation.start()
        self.main_window = None  # Referência à janela principal, definida externamente

    def update_layout(self):
        pixmap = self.pixmap()
        width = pixmap.width()
        height = pixmap.height()

        bar_width = width * 0.6
        self.progress_bar.setGeometry(
            int((width - bar_width) / 2),
            height - 60,
            int(bar_width),
            20
        )
        
        self.status_label.setGeometry(
            0,
            height - 90,
            width,
            30
        )

    def update_progress(self):
        self.progress += 25
        status_messages = {
            25: "Carregando módulos...",
            50: "Inicializando interface...",
            75: "Verificando conexões...",
            100: "Pronto!"
        }
        
        if self.progress in status_messages:
            self.status_label.setText(status_messages[self.progress])
        
        if self.progress >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self.finish_loading)

    def finish_loading(self):
        """Exibe a janela principal e fecha a splash screen"""
        if self.main_window and not self.main_window.isVisible():
            self.main_window.show()  # Exibe a janela principal apenas aqui
        self.close()

    def finish(self, main_window):
        """Associa a janela principal, mas não a exibe ainda"""
        self.main_window = main_window
        if self.progress >= 100:
            self.finish_loading()  # Se já terminou, exibe imediatamente

    def show(self):
        """Garante que a splash seja exibida apenas uma vez"""
        if not self.isVisible():
            super().show()