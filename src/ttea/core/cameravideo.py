import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


class CameraVideo(QThread):
    # Signal que vai disparar a cada novo frame capturado
    # Enviamos um QImage que o PySide6 consegue renderizar direto em um QLabel
    frame_ready = Signal(QImage)

    CAMERA_VIDEO_DEFAULT_WIDTH = 640
    CAMERA_VIDEO_DEFAULT_HEIGHT = 480

    def __init__(self, camera_index: int, use_low_resolution: bool = False):
        super().__init__()
        self.camera_index = camera_index
        self.use_low_resolution = use_low_resolution
        self.running = False
        self.cap = None
        self.service = CalibrationService()

    def run(self):
        """Método executado automaticamente quando chamamos o .start()"""
        # Inicializa a captura da câmera

        if self.service.is_windows():
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)
        else:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            self.error_signal.emit(
                self.tr("Não foi possível acessar a câmera selecionada.")
            )
            return

        # Define a resolução se não for "low_resolution"
        if not self.use_low_resolution:
            self.cap.set(
                cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_VIDEO_DEFAULT_WIDTH
            )
            self.cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_VIDEO_DEFAULT_HEIGHT
            )

        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # Se falhar ao ler o frame, quebra o loop (câmera desconectada, etc.)
                break

            # O OpenCV usa o padrão BGR, o PySide6 usa RGB. Precisamos converter!
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Pega as dimensões do frame
            height, width, channels = frame_rgb.shape
            bytes_per_line = channels * width

            # Converte o array do OpenCV (numpy) para o QImage do PySide6
            q_image = QImage(
                frame_rgb.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            )

            # Emite o sinal enviando a imagem para a interface principal
            self.frame_ready.emit(q_image)

        # Limpa os recursos ao sair do loop
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def stop(self):
        """Método para parar a thread de forma segura"""
        self.running = False
        self.wait()  # Aguarda a thread finalizar o ciclo atual
