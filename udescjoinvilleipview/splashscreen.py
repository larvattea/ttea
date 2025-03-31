from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from udescjoinvilleiputil.pathconfig import PathConfig
from udescjoinvilleipapp.ipapp import IPApp


class SplashScreen(QSplashScreen):
    def __init__(self):
        # Carrega a imagem do splash
        pixmap = QPixmap(PathConfig.image("ttealogo.png"))
        super().__init__(pixmap)
        
        # Configurações da janela
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Fundo transparente
        
        # Label de status
        self.status_label = QLabel("Iniciando...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            background: rgba(0, 0, 0, 150);
            padding: 5px;
        """)
        
        # Barra de progresso estilizada
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)  # Remove o texto padrão de porcentagem
        self.progress_bar.setRange(0, 100)
        
        # Estilo personalizado da barra
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
        
        # Posicionamento
        self.update_layout()
        
        # Animação da barra
        self.animation = QPropertyAnimation(self.progress_bar, b"value")
        self.animation.setDuration(3000)  # 3 segundos de duração
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # Curva suave
        
        # Timer para mensagens de status
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(750)  # Atualiza status a cada 0.75s
        
        # Inicia a animação
        self.animation.start()

    def update_layout(self):
        """Ajusta o layout dos elementos"""
        pixmap = self.pixmap()
        width = pixmap.width()
        height = pixmap.height()
        
        # Posiciona a barra de progresso
        bar_width = width * 0.6  # 60% da largura da imagem
        self.progress_bar.setGeometry(
            int((width - bar_width) / 2),  # Centraliza
            height - 60,                  # 60px acima do fundo
            int(bar_width),
            20
        )
        
        # Posiciona o label de status acima da barra
        self.status_label.setGeometry(
            0,
            height - 90,
            width,
            30
        )

    def update_progress(self):
        """Atualiza o status durante o carregamento"""
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
            QTimer.singleShot(500, self.finish_loading)  # Delay antes de fechar

    def finish_loading(self):
        """Finaliza o splash e abre a janela principal"""
        self.close()
        self.main_window = IPApp()
        self.main_window.show()