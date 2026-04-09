import cv2
import mediapipe as mp
import numpy as np

from udescjoinvilletteagames.kartea.gameutil import GameSettings

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_poses = mp.solutions.pose


class PoseTracking:
    """Responsável por detectar pose corporal usando MediaPipe e mapear pés para o jogo."""

    def __init__(self):
        self.settings = GameSettings()
        self.pose = mp_poses.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.results = None

        # Posições dos pés
        self.feet_x = 0
        self.feet_y = 0
        self.feet1_x = self.feet1_y = 0  # left heel
        self.feet2_x = self.feet2_y = 0  # right heel

        self.feet_closed = False

    def position(self, x: float, y: float):
        """Transforma coordenadas normalizadas da câmera para coordenadas do jogo usando perspectiva."""
        if len(self.settings.calibration_points) < 4:
            return (0, 0)

        pts1 = np.float32(
            [
                self.settings.calibration_points[0],
                self.settings.calibration_points[1],
                self.settings.calibration_points[2],
                self.settings.calibration_points[3],
            ]
        )

        pts2 = np.float32(
            [
                [0, 0],
                [self.settings.control_screen_width, 0],
                [0, self.settings.control_screen_height],
                [
                    self.settings.control_screen_width,
                    self.settings.control_screen_height,
                ],
            ]
        )

        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Ponto normalizado
        p = (
            int(x * self.settings.control_screen_width),
            int(y * self.settings.control_screen_height),
        )

        # Aplica transformação de perspectiva
        position_x = (
            matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2] + 1e-6)

        position_y = (
            matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2] + 1e-6)

        return (
            int(position_x * self.settings.width_ratio),
            int(position_y * self.settings.height_ratio),
        )

    def scan_feets(self, image):
        """Processa o frame e detecta posição dos pés."""
        if image is None:
            return image

        rows, cols, _ = image.shape

        # Converte para RGB e processa
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb_image.flags.writeable = False
        self.results = self.pose.process(rgb_image)
        rgb_image.flags.writeable = True

        # Converte de volta para BGR
        image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        self.feet_closed = False

        if self.results.pose_landmarks:
            # Landmark 30 = left heel, 29 = right heel
            self.feet1_x = self.results.pose_landmarks.landmark[30].x
            self.feet1_y = self.results.pose_landmarks.landmark[30].y
            self.feet2_x = self.results.pose_landmarks.landmark[29].x
            self.feet2_y = self.results.pose_landmarks.landmark[29].y

            # Ponto médio entre os calcanhares
            x = (self.feet1_x + self.feet2_x) / 2
            y = (self.feet1_y + self.feet2_y) / 2

            self.feet_x, self.feet_y = self.position(x, y)

            # Força movimento apenas horizontal (comum em jogos de pista)
            self.feet_y = self.settings.SCREEN_HEIGHT - 50

            # Desenha landmarks no frame de debug
            mp_drawing.draw_landmarks(
                image,
                self.results.pose_landmarks,
                mp_poses.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )

        return image

    def get_feet_center(self):
        """Retorna a posição central dos pés (usada para controlar o carro)."""
        return (self.feet_x, self.feet_y)

    def get_feet1(self):
        """Retorna posição do pé esquerdo."""
        return self.position(self.feet1_x, self.feet1_y)

    def get_feet2(self):
        """Retorna posição do pé direito."""
        return self.position(self.feet2_x, self.feet2_y)

    def close(self):
        """Libera recursos do MediaPipe (opcional)."""
        self.pose.close()
