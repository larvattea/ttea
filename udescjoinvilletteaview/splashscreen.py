# splashscreen.py → VERSÃO FINAL QUE FUNCIONA SEMPRE
from typing import Optional

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer, QTranslator
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QSplashScreen

from udescjoinvilletteautil import PathConfig


class SplashScreen(QSplashScreen):
    def __init__(self, translator: Optional["QTranslator"] = None):
        pixmap = QPixmap(PathConfig.image("ttealogo"))
        if pixmap.isNull():
            # Se a imagem não carregar, não trava tudo
            pixmap = QPixmap(600, 400)
            pixmap.fill(Qt.black)

        super().__init__(pixmap)
        self.setWindowFlags(
            Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Label de status
        self.status_label = QLabel(self.tr("Iniciando aplicação..."), self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                background: rgba(0, 0, 0, 160);
                padding: 8px;
                border-radius: 6px;
            }
        """
        )

        # Barra de progresso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # modo "indeterminado" enquanto anima
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background: rgba(0,0,0,180);
                height: 24px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:0.5 #00cc00, stop:1 #006600);
                border-radius: 3px;
            }
        """
        )

        self._update_geometry()

        # Animação infinita da barra (efeito "carregando")
        self.animation = QPropertyAnimation(self.progress_bar, b"value")
        self.animation.setDuration(2000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setLoopCount(-1)  # repete pra sempre
        self.animation.start()

        # Troca de mensagens a cada 1.2s
        self.messages = [
            self.tr("Iniciando aplicação..."),
            self.tr("Carregando módulos..."),
            self.tr("Inicializando interface..."),
            self.tr("Verificando configurações..."),
            self.tr("Quase lá..."),
        ]
        self.msg_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_message)
        self.timer.start(1200)

    def _update_geometry(self):
        w = self.width()
        h = self.height()
        bar_w = int(w * 0.7)
        self.progress_bar.setGeometry((w - bar_w) // 2, h - 70, bar_w, 24)
        self.status_label.setGeometry(0, h - 110, w, 40)

    def _next_message(self):
        self.status_label.setText(self.messages[self.msg_index])
        self.msg_index = (self.msg_index + 1) % len(self.messages)

    # MÉTODO CORRETO — NÃO SOBRESCREVA COM DUPLICATA!
    def finish(self, main_window):
        """Chamado pelo main.py — fecha o splash da forma correta"""
        self.timer.stop()
        self.animation.stop()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.status_label.setText(self.tr("Concluído!"))

        # O mais importante: chama o finish() original do Qt
        super().finish(main_window)

    # Garante que o layout acompanhe redimensionamento (opcional)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_geometry()
