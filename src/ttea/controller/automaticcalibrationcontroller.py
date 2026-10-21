from typing import TYPE_CHECKING, Dict, Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QCoreApplication, QObject, QRect, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap

from ttea.model import CalibrationPoint
from ttea.service import CalibrationService
from ttea.util import CvText, PathConfig

if TYPE_CHECKING:
    from ttea.view import AutomaticCalibrationView

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class AutomaticCalibrationController(QObject):
    msg_info_signal = Signal(str)
    msg_warning_signal = Signal(str)
    msg_critical_signal = Signal(str)

    close_view_signal = Signal()

    def __init__(
        self,
        view: "AutomaticCalibrationView",
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
        self.modo_preview = False
        self.monitor_screen: str = QCoreApplication.translate(
            "AutomaticCalibrationController", "Tela de Monitoramento"
        )
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        # ASCII key of the OpenCV window; the translated title (with
        # accents) is shown with CvText.set_window_title.
        self.monitor_window: str = CvText.window_name(self.monitor_screen)

        # ==================== MediaPipe Tasks (Pose Landmarker) =============
        if self.service.is_raspberry_pi():
            model_path = PathConfig.model(
                self.service.get_mediapipe_model_embedded()
            )
        else:
            model_path = PathConfig.model(
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
        self.pose_detector = vision.PoseLandmarker.create_from_options(options)
        # ========================================================================

        self.calibration_points = np.zeros((4, 2), dtype=np.int64)

    def numpy_to_pixmap(self, img: np.ndarray) -> QPixmap:
        """Converte um ndarray do OpenCV (Grayscale ou BGR) para QPixmap do PySide6."""
        if len(img.shape) == 2:  # Grayscale
            height, width = img.shape
            bytes_per_line = width
            q_img = QImage(
                img.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8,
            )
        else:  # BGR
            height, width, channels = img.shape
            bytes_per_line = channels * width
            q_img = QImage(
                img.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_BGR888,
            )

        return QPixmap.fromImage(q_img)

    def generate_board_pixmap(self) -> QPixmap:
        """
        Gera a imagem do tabuleiro ChArUco ajustada às dimensões do monitor/projetor
        e a converte para QPixmap para ser exibida na tela do PySide6.
        """
        screen_geometry = self.get_available_geometry_of_screen(
            self.monitor_index
        )
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        aruco_cols = self.service.get_automatic_num_columns()
        aruco_rows = self.service.get_automatic_num_rows()

        square_width = screen_width // aruco_cols
        square_height = screen_height // aruco_rows
        square_size_average = (square_width + square_height) / 2
        marker_size = int(
            square_size_average * self.service.get_automatic_multiplier()
        )

        aruco = cv2.aruco
        dictionary = aruco.getPredefinedDictionary(
            self.service.get_automatic_dictionary()
        )
        board = aruco.CharucoBoard(
            (aruco_cols, aruco_rows),
            square_size_average,
            marker_size,
            dictionary,
        )

        base_img = board.generateImage(
            (aruco_cols * 100, aruco_rows * 100),
            marginSize=self.service.get_automatic_margin(),
        )
        board_img = cv2.resize(
            base_img,
            (screen_width, screen_height),
            interpolation=cv2.INTER_NEAREST,
        )

        return self.numpy_to_pixmap(board_img)

    def _process_frame_geometry(
        self,
        frame: np.ndarray,
        detector: cv2.aruco.ArucoDetector,
        board: cv2.aruco.CharucoBoard,
        square_size_average: float,
        square_width: int,
        square_height: int,
        screen_width: int,
        screen_height: int,
    ) -> Optional[np.ndarray]:
        """
        Método auxiliar privado que processa um frame da câmera, detecta os marcadores
        ChArUco, estima a homografia e retorna os 4 vértices projetados da tela.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is None:
            return None

        try:
            retval, charuco_corners, charuco_ids = (
                cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)
            )

            if retval < 4:
                return None

            chess_corners = board.getChessboardCorners()
            src_points = []
            dst_points = []

            for corner_id, detected_corner in zip(
                charuco_ids.flatten(), charuco_corners
            ):
                world_pt = chess_corners[corner_id][:2]
                pixel_x = (world_pt[0] / square_size_average) * square_width
                pixel_y = (world_pt[1] / square_size_average) * square_height

                src_points.append([pixel_x, pixel_y])
                dst_points.append(detected_corner[0])

            src_pts = np.array(src_points, dtype=np.float32)
            dst_pts = np.array(dst_points, dtype=np.float32)

            H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if H is not None:
                rect_expandido = np.array(
                    [
                        [0, 0],
                        [screen_width, 0],
                        [0, screen_height],
                        [screen_width, screen_height],
                    ],
                    dtype=np.float32,
                ).reshape(-1, 1, 2)

                projected = cv2.perspectiveTransform(rect_expandido, H)
                return np.round(projected.reshape(4, 2)).astype(int)

        except Exception as e_charuco:
            mensagem = self.tr(
                "Aviso de detecção ChArUco.\nDetalhes: {0}"
            ).format(e_charuco)
            self.msg_warning_signal.emit(mensagem)

        return None

    def _draw_quadrilateral(
        self, img: np.ndarray, vertices: np.ndarray, with_labels: bool = False
    ) -> None:
        """Desenha o polígono e os pontos identificadores no frame."""
        render_pts = np.array(
            [vertices[0], vertices[1], vertices[3], vertices[2]],
            dtype=np.int32,
        )
        cv2.polylines(img, [render_pts], True, (0, 255, 255), 4)

        for pt in vertices:
            cv2.circle(img, (pt[0], pt[1]), 10, (0, 0, 255), -1)

        if with_labels:
            rotulos = [
                ("SE", vertices[0], (-25, -15)),
                ("SD", vertices[1], (15, -15)),
                ("IE", vertices[2], (-25, 25)),
                ("ID", vertices[3], (15, 25)),
            ]
            for texto, pt, offset in rotulos:
                pos_x, pos_y = pt[0] + offset[0], pt[1] + offset[1]
                cv2.putText(
                    img,
                    texto,
                    (pos_x, pos_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    3,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    img,
                    texto,
                    (pos_x, pos_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

    def start_auto_calibration(self) -> None:
        """Open the camera and the monitoring window, then poll frames.

        OpenCV windows must live on the GUI thread (Cocoa raises
        otherwise), so a QTimer drives ``_tick`` like the manual
        calibration does. The board itself is shown by the View.
        """
        try:
            screen_geometry = self.get_available_geometry_of_screen(
                self.monitor_index
            )
            self.screen_width = screen_geometry.width()
            self.screen_height = screen_geometry.height()

            aruco_cols = self.service.get_automatic_num_columns()
            aruco_rows = self.service.get_automatic_num_rows()

            self.square_width = self.screen_width // aruco_cols
            self.square_height = self.screen_height // aruco_rows
            self.square_size_average = (
                self.square_width + self.square_height
            ) / 2
            marker_size = int(
                self.square_size_average
                * self.service.get_automatic_multiplier()
            )

            dictionary = cv2.aruco.getPredefinedDictionary(
                self.service.get_automatic_dictionary()
            )
            self.board = cv2.aruco.CharucoBoard(
                (aruco_cols, aruco_rows),
                self.square_size_average,
                marker_size,
                dictionary,
            )
            self.detector = cv2.aruco.ArucoDetector(dictionary)

            self.camera = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )
            if not self.camera.isOpened():
                self.msg_critical_signal.emit(
                    self.tr("Não foi possível abrir a câmera.")
                )
                self.stop_auto_calibration()
                return

            self._open_monitor_window()
        except Exception as e:
            self._fail(e)
            return

        self.last_camera_vertices = None
        self.frozen_frame = None
        self.timer.start(30)

    def stop_auto_calibration(self) -> None:
        """Stop polling and release the camera and the OpenCV window."""
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        cv2.destroyAllWindows()

    def _open_monitor_window(self) -> None:
        cv2.namedWindow(self.monitor_window, cv2.WINDOW_AUTOSIZE)
        CvText.set_window_title(self.monitor_window, self.monitor_screen)

    def _fail(self, error: Exception) -> None:
        self.stop_auto_calibration()
        mensagem = self.tr(
            "Erro crítico na calibração automática.\nDetalhes: {0}."
        ).format(error)
        self.msg_critical_signal.emit(mensagem)

    def _camera_lost(self) -> None:
        self.stop_auto_calibration()
        self.msg_critical_signal.emit(
            self.tr(
                "Erro ao capturar imagem da câmera. Dispositivo desconectado.\nVerifique a conexão do cabo e/ou a instalação da câmera.\nFeche a janela e tente novamente."
            )
        )

    def _detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        return self._process_frame_geometry(
            frame,
            self.detector,
            self.board,
            self.square_size_average,
            self.square_width,
            self.square_height,
            self.screen_width,
            self.screen_height,
        )

    def _tick(self) -> None:
        """One iteration of the monitoring loop.

        The timer is paused while the iteration runs: message boxes
        and, on macOS, ``cv2.waitKey`` spin nested event loops that
        would otherwise re-enter it.
        """
        self.timer.stop()
        try:
            if self._step():
                self.timer.start(30)
        except Exception as e:
            self._fail(e)

    def _step(self) -> bool:
        """Show one frame and handle its key; False ends the loop."""
        if not self.modo_preview:
            ret, frame = self.camera.read()
            if not ret:
                self._camera_lost()
                return False

            vertices = self._detect(frame)
            if vertices is not None:
                self.last_camera_vertices = vertices
                self._draw_quadrilateral(frame, vertices)

            hud_lines = [
                self.tr("Tecle [S] para ocultar a tela e capturar a imagem."),
                self.tr("Tecle [ESC] para sair da tela de monitoramento."),
                self.tr(
                    "Tecle [ALT+F4 ou CMD+W] para fechar a tela das figuras."
                ),
            ]
            # Pillow instead of cv2.putText: accents (é, ó, ñ)
            # and wrapping of lines wider than the frame.
            display_frame = CvText.draw_lines(
                frame, hud_lines, origin=(20, 24)
            )
        else:
            msg_hud = self.tr(
                "Amostra: Tecle [ESC] para salvar | Tecle [R] para repetir."
            )
            display_frame = CvText.draw_lines(
                self.frozen_frame.copy(), [msg_hud], origin=(20, 24)
            )

        cv2.imshow(self.monitor_window, display_frame)
        key = cv2.waitKey(1) & 0xFF
        if self.camera is None:
            # Closed from an event handled inside waitKey
            return False

        if key in (ord("s"), ord("S")) and not self.modo_preview:
            # Hide the monitoring window so it does not cover the
            # board, then capture once it is gone.
            cv2.destroyWindow(self.monitor_window)
            cv2.waitKey(1)
            QTimer.singleShot(1000, self._capture_clean_frame)
            return False

        if key in (ord("r"), ord("R")) and self.modo_preview:
            self.modo_preview = False
            self.frozen_frame = None
            self.msg_warning_signal.emit(
                self.tr("Captura descartada. Rastreio reativado.")
            )
        elif key == 27:
            self.stop_auto_calibration()
            if self.modo_preview and self.last_camera_vertices is not None:
                self._save_vertices()
            else:
                self.msg_info_signal.emit(self.tr("Fechando sem salvar."))
            return False

        return True

    def _capture_clean_frame(self) -> None:
        """Read a frame without the monitoring window over the board."""
        if self.camera is None:  # Closed during the delay
            return
        try:
            # Drop buffered frames taken while the window was visible
            for _ in range(5):
                if not self.camera.grab():
                    self._camera_lost()
                    return

            ret, clean_frame = self.camera.read()
            if not ret:
                self._camera_lost()
                return

            clean_vertices = self._detect(clean_frame)
            self._open_monitor_window()
            if clean_vertices is not None:
                self.last_camera_vertices = clean_vertices
                self._draw_quadrilateral(
                    clean_frame, clean_vertices, with_labels=True
                )
                self.frozen_frame = clean_frame
                self.modo_preview = True
                self.msg_info_signal.emit(
                    self.tr("Sucesso! Captura realizada sem obstruções.")
                )
            else:
                self.msg_warning_signal.emit(
                    self.tr(
                        "O tabuleiro não pôde ser lido na foto limpa. Retornando..."
                    )
                )
        except Exception as e:
            self._fail(e)
            return
        self.timer.start(30)

    def _save_vertices(self) -> None:
        se, sd, ie, id_pt = self.last_camera_vertices

        if self.service.is_automatic_mirror_mode():
            largura_cam = self.frozen_frame.shape[1]
            self.calibration_points = np.array(
                [
                    [largura_cam - se[0], se[1]],  # SD
                    [largura_cam - sd[0], sd[1]],  # SE
                    [largura_cam - ie[0], ie[1]],  # ID
                    [largura_cam - id_pt[0], id_pt[1]],  # IE
                ],
                dtype=np.int64,
            )
        else:
            self.calibration_points = np.array(
                [sd, se, id_pt, ie], dtype=np.int64
            )

        self.create_calibration_point()

    def get_available_geometry_of_screen(
        self, monitor_index: Optional[int] = None
    ) -> Optional[QRect]:
        if monitor_index is None:
            monitor_index = self.monitor_index
        return self.service.get_available_geometry_of_screen(monitor_index)

    def create_calibration_point(self) -> None:
        data = self.get_data()
        if self.service.create_calibration_point(data):
            self.msg_info_signal.emit(
                self.tr("Calibração automática salva com sucesso!")
            )
        else:
            self.msg_critical_signal.emit(
                self.tr("Erro ao salvar os pontos da calibração automática.")
            )

    def get_data(self) -> Dict[str, int]:
        """Extrai os pontos de calibração utilizando as propriedades definidas no model."""
        flat_points = self.calibration_points.flatten().tolist()
        return {
            prop: int(val)
            for prop, val in zip(CalibrationPoint.PROPERTIES, flat_points)
        }
