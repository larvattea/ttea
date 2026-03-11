import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import \
    landmark_pb2  # Necessário para o desenho
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import pose as mp_pose
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QImage

from udescjoinvilletteaservice import CalibrationService


class CameraVideoThread(QThread, QObject):
    change_pixmap_signal = Signal(QImage)
    error_signal = Signal(str)

    CAMERA_VIDEO_THREAD_WIDTH = 640
    CAMERA_VIDEO_THREAD_HEIGHT = 480

    def __init__(self, camera_index: int, use_low_resolution: bool = False):
        from udescjoinvilletteacore import MediaPipeFilter, MediaPipeManager

        super().__init__()
        self.camera_index = camera_index
        self.running = True
        self.mp_manager = MediaPipeManager()
        self.use_low_resolution = use_low_resolution
        self.filter = MediaPipeFilter()
        self.service = CalibrationService()

    def _convert_to_proto(self, landmarks):
        """Converte landmarks da Task API para o formato esperado pelo draw_landmarks."""
        landmark_subset = landmark_pb2.NormalizedLandmarkList()
        for l in landmarks:
            landmark_subset.landmark.add(
                x=l.x, y=l.y, z=l.z, visibility=l.visibility
            )
        return landmark_subset

    def run(self):
        # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # Frame Dimensions & Speed: CAP_PROP_FRAME_WIDTH,
        # CAP_PROP_FRAME_HEIGHT, and CAP_PROP_FPS
        # Camera Settings: CAP_PROP_BRIGHTNESS, CAP_PROP_CONTRAST,
        # CAP_PROP_SATURATION, CAP_PROP_HUE, CAP_PROP_GAIN, and CAP_PROP_EXPOSURE.

        if self.service.is_windows():
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)
        else:
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        if not cap.isOpened():
            self.error_signal.emit(
                self.tr("Não foi possível acessar a câmera selecionada.")
            )
            return

        prev_time = 0

        # Se estiver no Windows com MX Brio, considere aumentar para 1280x720 para melhor precisão nos pés
        if self.use_low_resolution:
            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                CameraVideoThread.CAMERA_VIDEO_THREAD_WIDTH,
            )
            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                CameraVideoThread.CAMERA_VIDEO_THREAD_HEIGHT,
            )

        while self.running:
            success, frame = cap.read()

            if success:
                # 1. CÁLCULO DE BRILHO (Para debug de Luz Plena)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                avg_brightness = np.mean(hsv[:, :, 2])

                # 2. PRÉ-PROCESSAMENTO: Filtros Automáticos
                frame = self.filter.apply_enhancements(frame)

                # Cálculo de FPS
                curr_time = time.time()
                fps = (
                    1 / (curr_time - prev_time)
                    if (curr_time - prev_time) > 0
                    else 0
                )
                prev_time = curr_time

                # Preparação para MediaPipe
                timestamp = int(time.time() * 1000)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB, data=rgb_frame
                )

                # Processamento MediaPipe
                result = self.mp_manager.detect(mp_image, timestamp)

                if result.pose_landmarks:
                    # Suavização (agora aplicada a todos os pontos se desejar)
                    result.pose_landmarks = self.filter.smooth_landmarks(
                        result.pose_landmarks
                    )

                    for landmarks in result.pose_landmarks:
                        # Desenha Esqueleto Completo
                        mp_drawing.draw_landmarks(
                            frame,
                            self._convert_to_proto(landmarks),
                            mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing.DrawingSpec(
                                color=(0, 255, 0), thickness=2, circle_radius=2
                            ),
                            connection_drawing_spec=mp_drawing.DrawingSpec(
                                color=(255, 255, 255), thickness=2
                            ),
                        )

                        # Exibe Confiança dos Pés (Índices 31 e 32)
                        conf_esq = landmarks[31].visibility
                        conf_dir = landmarks[32].visibility
                        c_color = (
                            (0, 255, 0)
                            if (conf_esq + conf_dir) / 2 > 0.5
                            else (0, 0, 255)
                        )
                        cv2.putText(
                            frame,
                            f"Conf. Pes: {(conf_esq + conf_dir)/2:.2f}",
                            (15, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            c_color,
                            2,
                        )

                # UI de Telemetria
                fps_color = (0, 255, 0) if fps >= 15 else (0, 0, 255)
                cv2.putText(
                    frame,
                    f"FPS: {int(fps)}",
                    (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    fps_color,
                    2,
                )
                # print(f"FPS: {int(fps)}")
                cv2.putText(
                    frame,
                    f"Brilho: {int(avg_brightness)}",
                    (15, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2,
                )

                # Conversão para PySide
                display_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = display_rgb.shape
                qt_img = QImage(
                    display_rgb.data, w, h, ch * w, QImage.Format_RGB888
                )
                self.change_pixmap_signal.emit(qt_img.copy())
            else:
                self.error_signal.emit(
                    self.tr("A conexão com a câmera foi interrompida.")
                )
                break

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
