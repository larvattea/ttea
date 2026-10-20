"""Controller of the automatic calibration with a ChArUco board."""

import time
from typing import TYPE_CHECKING, Dict, Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QCoreApplication, QObject, QRect, Signal
from PySide6.QtGui import QImage, QPixmap

from ttea.model import CalibrationPoint
from ttea.service import CalibrationService
from ttea.util import CvText, PathConfig

if TYPE_CHECKING:
    from ttea.view import AutomaticCalibrationView

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class AutomaticCalibrationController(QObject):
    """Controller of the automatic calibration.

    The view shows a ChArUco board on the projection screen; this
    controller reads the camera, detects the board, estimates where the
    screen corners are in the camera image and saves them as
    ``CalibrationPoint``.

    Parameters
    ----------
    view : AutomaticCalibrationView
        The automatic calibration dialog.
    camera_index : int
        OpenCV index of the camera.
    monitor_index : int
        Index of the projection screen.
    service : CalibrationService | None, optional
        Calibration service. Default is None, which creates a new
        ``CalibrationService``.

    Attributes
    ----------
    msg_info_signal : Signal(str)
        Emitted with a translated information message.
    msg_warning_signal : Signal(str)
        Emitted with a translated warning message.
    msg_critical_signal : Signal(str)
        Emitted with a translated error message.
    close_view_signal : Signal()
        Declared for the view; not emitted by this class.
    view : AutomaticCalibrationView
        The automatic calibration dialog.
    service : CalibrationService
        Calibration service (settings and saving).
    monitor_index : int
        Index of the projection screen.
    camera_index : int
        OpenCV index of the camera.
    camera : None
        Not used: ``run_auto_calibration`` opens its own capture.
    modo_preview : bool
        True while a captured sample is shown for confirmation.
    monitor_screen : str
        Translated title of the OpenCV window.
    monitor_window : str
        ASCII name of the OpenCV window (``CvText.window_name``).
    pose_detector : vision.PoseLandmarker
        MediaPipe pose landmarker, configured from the settings.
    calibration_points : numpy.ndarray
        ``(4, 2)`` int64 array with the corners to save.

    Notes
    -----
    Messages are sent through the signals so the view shows them. The
    window title is translated with ``QCoreApplication.translate`` in
    the ``"AutomaticCalibrationController"`` context, and messages with
    ``self.tr()``.
    """

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
        # ASCII key of the OpenCV window; the translated title (with
        # accents) is shown with CvText.set_window_title.
        self.monitor_window: str = CvText.window_name(self.monitor_screen)

        # MediaPipe Tasks (Pose Landmarker)
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

        self.calibration_points = np.zeros((4, 2), dtype=np.int64)

    def numpy_to_pixmap(self, img: np.ndarray) -> QPixmap:
        """Convert an OpenCV image to a ``QPixmap``.

        Parameters
        ----------
        img : numpy.ndarray
            Grayscale (2-D) or BGR (3-D) ``uint8`` image.

        Returns
        -------
        QPixmap
            The image as a pixmap.
        """
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
        """Create the ChArUco board image for the screen.

        Returns
        -------
        QPixmap
            Board with ``get_automatic_num_columns()`` by
            ``get_automatic_num_rows()`` squares, stretched to the
            available screen size.

        Notes
        -----
        The square size is the mean of the screen width per column and
        the screen height per row; the marker size is that value times
        ``get_automatic_multiplier()``. The board is drawn at 100 px per
        square with ``get_automatic_margin()`` and resized with nearest
        neighbor interpolation.
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
        """Return the screen corners found in a camera frame.

        Detects the ArUco markers, interpolates the ChArUco corners,
        estimates the homography from board to camera (RANSAC, 5 px) and
        projects the screen corners with it.

        Returns
        -------
        numpy.ndarray | None
            ``(4, 2)`` int array with the camera positions of the screen
            corners top-left, top-right, bottom-left, bottom-right; None
            if fewer than 4 ChArUco corners are found or the homography
            fails.

        Notes
        -----
        ChArUco errors are reported through ``msg_warning_signal``.
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
        """Draw the detected screen outline and corners on a frame.

        With ``with_labels``, the corners are labeled SE, SD, IE, ID
        (Portuguese for top-left, top-right, bottom-left, bottom-right).
        """
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

    def run_auto_calibration(self) -> None:
        """Detect the board in the camera and save the corners.

        Notes
        -----
        Keys in the OpenCV window:

        - S: close the window, wait 1 s, discard 5 buffered frames and
          detect the board on a clean frame; on success, show it as a
          sample (preview mode).
        - R: discard the sample and resume tracking.
        - ESC: save the sample corners (if any) and finish; without a
          sample, finish without saving.

        The corners are saved as the screen's top-right, top-left,
        bottom-right, bottom-left corners in the camera image. With
        ``is_automatic_mirror_mode()``, the x coordinates become ``frame
        width - x``, so the saved order is the same in the mirrored
        image. TODO(doc): the manual calibration saves the clicks as
        top-left, top-right, bottom-left, bottom-right; is the different
        order intended?

        Errors are reported through ``msg_critical_signal``; the camera
        is released and all OpenCV windows are closed at the end.
        """
        cap = None
        try:
            # --- Screen metrics ---
            screen_geometry = self.get_available_geometry_of_screen(
                self.monitor_index
            )
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()

            # --- ChArUco board ---
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

            # --- Camera ---
            cap = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )
            if not cap.isOpened():
                self.msg_critical_signal.emit(
                    self.tr("Não foi possível abrir a câmera.")
                )
                return

            detector = aruco.ArucoDetector(dictionary)
            cv2.namedWindow(self.monitor_window, cv2.WINDOW_AUTOSIZE)
            CvText.set_window_title(self.monitor_window, self.monitor_screen)

            last_camera_vertices = None
            frozen_frame = None

            # --- Main loop ---
            while True:
                if not self.modo_preview:
                    if not cap.isOpened():
                        self.msg_critical_signal.emit(
                            self.tr("Não foi possível abrir a câmera.")
                        )
                        break

                    ret, frame = cap.read()
                    if not ret:
                        self.msg_critical_signal.emit(
                            self.tr(
                                "Erro ao capturar imagem da câmera. Dispositivo desconectado.\nVerifique a conexão do cabo e/ou a instalação da câmera.\nFeche a janela e tente novamente."
                            )
                        )
                        break

                    vertices = self._process_frame_geometry(
                        frame,
                        detector,
                        board,
                        square_size_average,
                        square_width,
                        square_height,
                        screen_width,
                        screen_height,
                    )

                    if vertices is not None:
                        last_camera_vertices = vertices
                        self._draw_quadrilateral(frame, vertices)

                    display_frame = frame.copy()
                    hud_lines = [
                        self.tr(
                            "Tecle [S] para ocultar a tela e capturar a imagem."
                        ),
                        self.tr(
                            "Tecle [ESC] para sair da tela de monitoramento."
                        ),
                        self.tr(
                            "Tecle [ALT+F4 ou CMD+W] para fechar a tela das figuras."
                        ),
                    ]

                    # Pillow instead of cv2.putText: accents (é, ó, ñ)
                    # and wrapping of lines wider than the frame.
                    display_frame = CvText.draw_lines(
                        display_frame, hud_lines, origin=(20, 24)
                    )
                else:
                    display_frame = frozen_frame.copy()
                    msg_hud = self.tr(
                        "Amostra: Tecle [ESC] para salvar | Tecle [R] para repetir."
                    )
                    display_frame = CvText.draw_lines(
                        display_frame, [msg_hud], origin=(20, 24)
                    )

                cv2.imshow(self.monitor_window, display_frame)
                key = cv2.waitKey(1) & 0xFF

                # --- S: hide the window and take a clean capture ---
                if (
                    key == ord("s") or key == ord("S")
                ) and not self.modo_preview:
                    cv2.destroyWindow(self.monitor_window)
                    cv2.waitKey(1)

                    time.sleep(1.0)

                    # Drop buffered frames; a failed grab means the
                    # camera was disconnected.
                    buffer_ok = True
                    for _ in range(5):
                        if not cap.grab():
                            buffer_ok = False
                            break

                    if not buffer_ok:
                        self.msg_critical_signal.emit(
                            self.tr(
                                "Erro ao capturar imagem da câmera. Dispositivo desconectado.\nVerifique a conexão do cabo e/ou a instalação da câmera.\nFeche a janela e tente novamente."
                            )
                        )
                        break

                    ret, clean_frame = cap.read()

                    if ret:
                        clean_vertices = self._process_frame_geometry(
                            clean_frame,
                            detector,
                            board,
                            square_size_average,
                            square_width,
                            square_height,
                            screen_width,
                            screen_height,
                        )

                        if clean_vertices is not None:
                            last_camera_vertices = clean_vertices
                            self._draw_quadrilateral(
                                clean_frame, clean_vertices, with_labels=True
                            )
                            frozen_frame = clean_frame.copy()
                            self.modo_preview = True
                            self.msg_info_signal.emit(
                                self.tr(
                                    "Sucesso! Captura realizada sem obstruções."
                                )
                            )
                        else:
                            self.msg_warning_signal.emit(
                                self.tr(
                                    "O tabuleiro não pôde ser lido na foto limpa. Retornando..."
                                )
                            )
                    else:
                        self.msg_critical_signal.emit(
                            self.tr(
                                "Erro ao capturar imagem da câmera. Dispositivo desconectado.\nVerifique a conexão do cabo e/ou a instalação da câmera.\nFeche a janela e tente novamente."
                            )
                        )
                        break

                    cv2.namedWindow(self.monitor_window, cv2.WINDOW_AUTOSIZE)
                    CvText.set_window_title(
                        self.monitor_window, self.monitor_screen
                    )

                # --- R: back to live tracking ---
                elif (
                    key == ord("r") or key == ord("R")
                ) and self.modo_preview:
                    self.modo_preview = False
                    frozen_frame = None
                    self.msg_warning_signal.emit(
                        self.tr("Captura descartada. Rastreio reativado.")
                    )

                # --- ESC: save and close ---
                elif key == 27:
                    if self.modo_preview and last_camera_vertices is not None:
                        se, sd, ie, id_pt = last_camera_vertices

                        if self.service.is_automatic_mirror_mode():
                            largura_cam = frozen_frame.shape[1]
                            self.calibration_points = np.array(
                                [
                                    [largura_cam - se[0], se[1]],  # TR
                                    [largura_cam - sd[0], sd[1]],  # TL
                                    [largura_cam - ie[0], ie[1]],  # BR
                                    [largura_cam - id_pt[0], id_pt[1]],  # BL
                                ],
                                dtype=np.int64,
                            )
                        else:
                            self.calibration_points = np.array(
                                [sd, se, id_pt, ie], dtype=np.int64
                            )

                        self.create_calibration_point()
                    else:
                        self.msg_info_signal.emit(
                            self.tr("Fechando sem salvar.")
                        )
                    break

        except Exception as e:
            mensagem = self.tr(
                "Erro crítico na calibração automática.\nDetalhes: {0}."
            ).format(e)
            self.msg_critical_signal.emit(mensagem)
        finally:
            if cap is not None and cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()

    def get_available_geometry_of_screen(
        self, monitor_index: Optional[int] = None
    ) -> Optional[QRect]:
        """Return the available geometry of a screen.

        Parameters
        ----------
        monitor_index : int | None, optional
            Screen index. Default is None, which uses ``monitor_index``.

        Returns
        -------
        QRect | None
            The available geometry, or None if the index is out of
            range.
        """
        if monitor_index is None:
            monitor_index = self.monitor_index
        return self.service.get_available_geometry_of_screen(monitor_index)

    def create_calibration_point(self) -> None:
        """Save the corners and report the result."""
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
        """Return the corners as ``CalibrationPoint`` field values.

        Returns
        -------
        dict[str, int]
            ``pointx1``, ``pointy1``... ``pointy4`` from
            ``calibration_points``.
        """
        flat_points = self.calibration_points.flatten().tolist()
        return {
            prop: int(val)
            for prop, val in zip(CalibrationPoint.PROPERTIES, flat_points)
        }
