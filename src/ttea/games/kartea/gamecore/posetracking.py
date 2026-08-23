import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# from settings import *
# import settings as st
from ttea.games.kartea.gameutil import GameSettings
from ttea.games.kartea.service import PlayerKarteaConfigService
from ttea.games.kartea.util import KarteaPathConfig

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_poses = mp.solutions.pose


class PoseTracking:
    """Classe responsável pela detecção de pose corporal usando MediaPipe, com foco nos pés."""

    def __init__(self):
        self.service = PlayerKarteaConfigService()
        # ==================== MediaPipe Tasks (Pose Landmarker) =============
        if self.service.is_raspberry_pi():
            model_path = KarteaPathConfig.model(
                self.service.get_mediapipe_model_embedded()
            )
        else:
            model_path = KarteaPathConfig.model(
                self.service.get_mediapipe_model_desktop()
            )

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=self.service.get_mediapipe_execution_mode(),
            num_poses=self.service.get_mediapipe_num_position(),
            min_pose_detection_confidence=self.service.get_mediapipe_detection_position(),
            min_pose_presence_confidence=self.service.get_mediapipe_detection_presence(),
            min_tracking_confidence=self.service.get_mediapipe_detection_tracking(),
        )

        self.pose_tracking = vision.PoseLandmarker.create_from_options(options)

        # Variáveis de posição dos pés
        self.feet_x = 0
        self.feet_y = 0
        self.feet1_x = 0
        self.feet1_y = 0
        self.feet2_x = 0
        self.feet2_y = 0

        self.results = None
        self.feet_closed = (
            False
            # Mantido como no original (apesar do método vazio)
        )
        self.last_timestamp_ms = 0

    def scan_feets(self, image):
        """
        Processa o frame da câmera, detecta os pés e retorna a imagem anotada.

        Args:
            image: Frame capturado pela câmera (BGR)

        Returns:
            Imagem processada com landmarks desenhados
        """
        rows, cols, _ = image.shape

        # Converte BGR para RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Envelopa a imagem no formato esperado pelo Tasks API
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1
        self.last_timestamp_ms = timestamp_ms

        self.results = self.pose_tracking.detect_for_video(
            mp_image, timestamp_ms
        )

        self.feet_closed = False

        if (
            self.results.pose_landmarks
            and len(self.results.pose_landmarks) > 0
        ):
            landmarks = self.results.pose_landmarks[0]
            # Landmark 30 = left heel, Landmark 29 = right heel
            self.feet1_x = landmarks[30].x
            self.feet1_y = landmarks[30].y
            self.feet2_x = landmarks[29].x
            self.feet2_y = landmarks[29].y

            # Calcula ponto central entre os dois pés
            x = (self.feet1_x + self.feet2_x) / 2
            y = (self.feet1_y + self.feet2_y) / 2

            # Converte coordenadas usando transformação de perspectiva
            self.feet_x, self.feet_y = self.posicao(x, y)

            # Força a posição Y fixa (movimento apenas lateral)
            self.feet_y = GameSettings.SCREEN_HEIGHT - 50

            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend(
                [
                    landmark_pb2.NormalizedLandmark(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z,
                        visibility=landmark.visibility,
                        presence=landmark.presence,
                    )
                    for landmark in landmarks
                ]
            )

            # Desenha os landmarks na imagem
            mp_drawing.draw_landmarks(
                image,
                pose_landmarks_proto,
                mp_poses.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )

        return image

    def get_feet_center(self):
        """Retorna a posição central dos pés (usada para controlar o carro)."""
        return (self.feet_x, self.feet_y)

    def get_feet1(self):
        """Retorna a posição do pé esquerdo (heel)."""
        return self.posicao(self.feet1_x, self.feet1_y)

    def get_feet2(self):
        """Retorna a posição do pé direito (heel)."""
        return self.posicao(self.feet2_x, self.feet2_y)

    def display_feet(self):
        """Exibe a imagem processada (método mantido do original)."""
        if hasattr(self, "image") and self.image is not None:
            cv2.imshow("image", self.image)
            cv2.waitKey(1)

    def is_feet_closed(self):
        """Método reservado para detecção de pés fechados (ainda não implementado no original)."""
        pass

    def posicao(self, x: float, y: float):
        """
        Aplica transformação de perspectiva para mapear a posição do jogador
        da câmera para as coordenadas do jogo.
        """
        pts1 = np.float32(
            [
                GameSettings.pontos_calibracao[0],
                GameSettings.pontos_calibracao[1],
                GameSettings.pontos_calibracao[2],
                GameSettings.pontos_calibracao[3],
            ]
        )
        pts2 = np.float32(
            [
                [0, 0],
                [GameSettings.largura_tela_controle, 0],
                [0, GameSettings.altura_tela_controle],
                [
                    GameSettings.largura_tela_controle,
                    GameSettings.altura_tela_controle,
                ],
            ]
        )

        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Posição normalizada do jogador
        p = (
            int(x * GameSettings.largura_tela_controle),
            int(y * GameSettings.altura_tela_controle),
        )

        # Aplica a transformação de perspectiva
        position_x = (
            matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])
        position_y = (
            matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]
        ) / (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2])

        # Converte para as dimensões reais da tela do jogo
        p_after = (
            int(position_x * GameSettings.relacao_largura),
            int(position_y * GameSettings.relacao_altura),
        )

        return p_after
