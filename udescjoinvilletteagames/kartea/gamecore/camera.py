import cv2

from udescjoinvilletteagames.kartea.gameutil import GameSettings


class Camera:
    """Gerencia a captura de vídeo da câmera."""

    def __init__(self):
        self.settings = GameSettings()
        self.cap = None
        self.frame = None
        self.ret = False
        self._initialize_camera()

    def _initialize_camera(self):
        """Inicializa a captura de vídeo."""
        self.cap = cv2.VideoCapture(self.settings.CAMERA, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Erro: Não foi possível abrir a câmera.")
            return
        self.ret, self.frame = self.cap.read()

    def load_camera(self):
        """Lê um frame, aplica flip e desenha a área de calibração."""
        if self.cap is None or not self.cap.isOpened():
            return None

        self.ret, self.frame = self.cap.read()
        if not self.ret or self.frame is None:
            return None

        # Flip horizontal (efeito espelho)
        self.frame = cv2.flip(self.frame, 1)

        # Desenha a área de calibração
        pts = self.settings.calibration_points
        if len(pts) >= 4:
            cv2.line(self.frame, pts[0], pts[1], self.settings.green, 2)
            cv2.line(self.frame, pts[1], pts[3], self.settings.green, 2)
            cv2.line(self.frame, pts[2], pts[0], self.settings.green, 2)
            cv2.line(self.frame, pts[2], pts[3], self.settings.green, 2)

            for point in pts:
                cv2.circle(self.frame, point, 5, self.settings.blue, 3)

        cv2.imshow("Tela de Captura", self.frame)
        cv2.waitKey(1)
        return self.frame

    def close_camera(self):
        """Libera a câmera e fecha a janela."""
        if self.cap is not None:
            self.cap.release()
        # cv2.destroyWindow("Tela de Captura")
        try:
            if (
                cv2.getWindowProperty("Tela de Captura", cv2.WND_PROP_VISIBLE)
                >= 0
            ):
                cv2.destroyWindow("Tela de Captura")
        except Exception:
            pass  # ignora se a janela não existir

        cv2.destroyAllWindows()
