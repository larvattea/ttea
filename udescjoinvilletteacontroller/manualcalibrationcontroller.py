from typing import TYPE_CHECKING, Dict, Optional, Union

import cv2
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QCoreApplication, QObject, QRect, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QPixmap

from udescjoinvilletteamodel import AppModel, Language
from udescjoinvilletteaservice import CalibrationService
from udescjoinvilletteautil import PathConfig

if TYPE_CHECKING:
    from udescjoinvilletteaview import ManualCalibrationView


class ManualCalibrationController(QObject):

    MONITOR_SCREEN: str = QCoreApplication.translate(
        "ManualCalibrationController", "Tela de Monitoramento"
    )

    def __init__(
        self,
        view: "ManualCalibrationView",
        camera_index: int,
        monitor_index: int,
        service: Optional[CalibrationService] = None,
    ):
        super().__init__()
        self.view = view
        self.service = service or CalibrationService()
        self.monitor_index = monitor_index
        self.camera_index = camera_index
        self.camera = None

        # ==================== MediaPipe Tasks (Pose Landmarker) =============
        model_path = PathConfig.model("pose_landmarker_full.task")
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.pose_detector = vision.PoseLandmarker.create_from_options(options)
        self.frame_timestamp = 0
        # ========================================================================

        self.calibration_points = np.zeros(
            (4, 2), dtype=np.int64
        )  # 4 pontos de calibração
        self.click_calibration_count = 0

        language_app = AppModel.get_instance().current_language
        for lang in Language.LANGUAGES:
            if language_app == lang["code"]:
                self._load_image(f"warning{lang['code'][:2]}")
                break

        # self._load_image("warningpt")
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self._update_camera_feed)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_C:
            # Troca para imagem de calibração
            self._load_image("calibrationpt")

            # Inicia a câmera (se ainda não estiver aberta)
            if self.camera is None or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(
                    self.camera_index, cv2.CAP_DSHOW
                )
                if self.camera.isOpened():
                    cv2.namedWindow(self.MONITOR_SCREEN, cv2.WINDOW_NORMAL)
                    cv2.setMouseCallback(
                        self.MONITOR_SCREEN,
                        self._mouse_click_callback,
                    )
                    self.camera_timer.start(30)  # ~33 FPS
                else:
                    self.view.msg.critical(
                        self.tr("Não foi possível abrir a câmera.")
                    )
                    self.camera = None

        elif event.key() == Qt.Key_Q:
            self.view.close()

    def _mouse_click_callback(self, event, x, y, flags, param):
        """Callback para capturar cliques na janela da câmera"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.click_calibration_count < 4:
                self.calibration_points[self.click_calibration_count] = [x, y]
                self.click_calibration_count += 1
                print(
                    f"Ponto {self.click_calibration_count} capturado: ({x}, {y})"
                )

                if self.click_calibration_count == 4:
                    self._load_image("calibrationokpt")
                    self.view.msg.info(
                        self.tr("Calibração concluída com sucesso!")
                    )

    def _load_image(self, image_name: str):
        """Carrega imagem via utilitário e exibe centralizada"""

        qimage = PathConfig.image(image_name)
        pixmap = QPixmap(qimage)
        self.view.lbl_image.setPixmap(pixmap)

    def _update_camera_feed(self):
        """Atualiza o feed da câmera na janela do OpenCV"""
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                control_screen = cv2.cvtColor(
                    cv2.flip(frame, 1), cv2.COLOR_BGR2RGB
                )
                control_screen.flags.writeable = False

                # Processamento com MediaPipe Pose
                # results = self.pose.process(control_screen)

                control_screen.flags.writeable = True
                control_screen = cv2.cvtColor(
                    control_screen, cv2.COLOR_RGB2BGR
                )

                for i in range(4):
                    cv2.circle(
                        control_screen,
                        tuple(self.calibration_points[i]),
                        8,
                        (255, 0, 0),  # Azul
                        -1,
                    )

                if self.click_calibration_count == 4:
                    pts = self.calibration_points
                    cv2.line(
                        control_screen,
                        tuple(pts[0]),
                        tuple(pts[1]),
                        (0, 255, 0),
                        2,
                    )  # Verde
                    cv2.line(
                        control_screen,
                        tuple(pts[1]),
                        tuple(pts[3]),
                        (0, 255, 0),
                        2,
                    )
                    cv2.line(
                        control_screen,
                        tuple(pts[2]),
                        tuple(pts[0]),
                        (0, 255, 0),
                        2,
                    )
                    cv2.line(
                        control_screen,
                        tuple(pts[2]),
                        tuple(pts[3]),
                        (0, 255, 0),
                        2,
                    )

                cv2.imshow(self.MONITOR_SCREEN, control_screen)

            else:
                self.view.msg.critical(
                    self.tr("Falha ao capturar imagem da câmera.")
                )

    def get_available_geometry_of_screen(self) -> Optional[QRect]:
        available_geo = self.service.get_available_geometry_of_screen(
            self.monitor_index
        )
        return available_geo

    def create_calibration_point(self) -> None:
        data = self.get_data()
        if self.service.create_calibration_point(data):
            self.view.msg.info(
                self.tr("Calibração manual cadastrada com sucesso!")
            )
        else:
            self.view.msg.critical(
                self.tr("Erro ao salvar os pontos da calibração manual.")
            )

    def get_data(self) -> Dict[str, Union[str, int]]:
        """Extract current form values into a dictionary.

        Returns
        -------
        dict
            Mapping with keys:
            - "id": int from model or init with zero
            - "name": str from name input
            - "birth_date": date from date editor
            - "observation": str from observation text area
        """
        return {
            "pointx1": self.calibration_points[0][0],
            "pointy1": self.calibration_points[0][1],
            "pointx2": self.calibration_points[1][0],
            "pointy2": self.calibration_points[1][1],
            "pointx3": self.calibration_points[2][0],
            "pointy3": self.calibration_points[2][1],
            "pointx4": self.calibration_points[3][0],
            "pointy4": self.calibration_points[3][1],
        }
