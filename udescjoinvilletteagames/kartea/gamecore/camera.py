import cv2

# import settings


class Camera:
    """Classe responsável pelo gerenciamento da câmera (captura de vídeo via OpenCV)."""

    def __init__(self):
        """Inicializa a captura de vídeo usando a configuração definida em settings."""
        self.cap = cv2.VideoCapture(settings.CAMERA, cv2.CAP_DSHOW)
        self.ret = False
        self.frame = None

        # Lê o primeiro frame para inicialização
        self.ret, self.frame = self.cap.read()

    def load_camera(self):
        """
        Lê um novo frame da câmera, aplica flip horizontal e desenha
        a área de calibração na imagem.
        """
        self.ret, self.frame = self.cap.read()

        if self.frame is not None:
            # Espelha a imagem horizontalmente (efeito mirror)
            self.frame = cv2.flip(self.frame, 1)

            # Desenha as linhas da área de calibração
            cv2.line(
                self.frame,
                settings.pontos_calibracao[0],
                settings.pontos_calibracao[1],
                settings.verde,
                2,
            )

            cv2.line(
                self.frame,
                settings.pontos_calibracao[1],
                settings.pontos_calibracao[3],
                settings.verde,
                2,
            )

            cv2.line(
                self.frame,
                settings.pontos_calibracao[2],
                settings.pontos_calibracao[0],
                settings.verde,
                2,
            )

            cv2.line(
                self.frame,
                settings.pontos_calibracao[2],
                settings.pontos_calibracao[3],
                settings.verde,
                2,
            )

            # Desenha os pontos de calibração como círculos
            cv2.circle(
                self.frame, settings.pontos_calibracao[0], 5, settings.azul, 3
            )
            cv2.circle(
                self.frame, settings.pontos_calibracao[1], 5, settings.azul, 3
            )
            cv2.circle(
                self.frame, settings.pontos_calibracao[2], 5, settings.azul, 3
            )
            cv2.circle(
                self.frame, settings.pontos_calibracao[3], 5, settings.azul, 3
            )

            # Exibe a janela de captura
            cv2.imshow("Tela de Captura", self.frame)

    def close_camera(self):
        """Libera a câmera e fecha a janela de captura."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyWindow("Tela de Captura")
