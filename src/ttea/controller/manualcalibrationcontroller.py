"""Controller of the manual calibration: corners clicked by the user."""

from typing import TYPE_CHECKING, Dict, Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QCoreApplication, QObject, QRect, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QPixmap

from ttea.model import AppModel, CalibrationPoint, Language
from ttea.service import CalibrationService
from ttea.util import CvText, PathConfig

if TYPE_CHECKING:
    from ttea.view import ManualCalibrationView

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class ManualCalibrationController(QObject):
    """Controller of the manual calibration.

    Shows the camera image, with the detected skeleton, in an OpenCV
    window where the user clicks the four corners of the projected area,
    and saves them as ``CalibrationPoint``.

    Parameters
    ----------
    view : ManualCalibrationView
        The manual calibration dialog.
    camera_index : int
        OpenCV index of the camera.
    monitor_index : int
        Index of the projection screen.
    service : CalibrationService | None, optional
        Calibration service. Default is None, which creates a new
        ``CalibrationService``.

    Attributes
    ----------
    view : ManualCalibrationView
        The manual calibration dialog.
    service : CalibrationService
        Calibration service (settings and saving).
    monitor_index : int
        Index of the projection screen.
    camera_index : int
        OpenCV index of the camera.
    camera : cv2.VideoCapture | None
        Open camera, or None before the user presses C.
    monitor_screen : str
        Translated title of the OpenCV window.
    monitor_window : str
        ASCII name of the OpenCV window (``CvText.window_name``).
    pose_detector : vision.PoseLandmarker
        MediaPipe pose landmarker, configured from the settings.
    frame_timestamp : int
        Timestamp in ms passed to ``detect_for_video``.
    calibration_points : numpy.ndarray
        ``(4, 2)`` int64 array with the clicked corners, in click order.
    click_calibration_count : int
        Number of corners clicked so far (0 to 4).
    language_app : str
        Current language code, used to pick the instruction images.
    camera_timer : QTimer
        Timer that refreshes the camera window (every 30 ms).

    Notes
    -----
    Keys: C starts the camera and shows the calibration image; Q closes
    the dialog. The corners are camera pixel coordinates, taken after
    the optional mirroring (``is_manual_mirror_mode``). The outline
    drawn after the fourth click joins 1-2, 2-4, 3-1 and 3-4, i.e. the
    expected click order is top-left, top-right, bottom-left,
    bottom-right.

    The instruction images are chosen by the language prefix
    (``warning<xx>``, ``calibration<xx>``, ``calibrationok<xx>``). The
    window title is translated with ``QCoreApplication.translate`` in
    the ``"ManualCalibrationController"`` context, and messages with
    ``self.tr()``.
    """

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
        self.monitor_screen: str = QCoreApplication.translate(
            "ManualCalibrationController", "Tela de Monitoramento"
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
        self.frame_timestamp = 0

        self.calibration_points = np.zeros((4, 2), dtype=np.int64)
        self.click_calibration_count = 0

        self.language_app = AppModel.get_instance().current_language
        for lang in Language.LANGUAGES:
            if self.language_app == lang["code"]:
                self._load_image(f"warning{lang['code'][:2]}")
                break

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self._update_camera_feed)

    def _setup_calibration_window(self):
        """Open the OpenCV window and bind the mouse callback."""
        cv2.namedWindow(self.monitor_window, cv2.WINDOW_NORMAL)
        CvText.set_window_title(self.monitor_window, self.monitor_screen)
        cv2.setMouseCallback(self.monitor_window, self._mouse_click_callback)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle the keys of the calibration dialog.

        Parameters
        ----------
        event : QKeyEvent
            Key event forwarded by the view: C starts the camera (and
            the refresh timer) and Q closes the dialog.
        """
        if event.key() == Qt.Key_C:
            for lang in Language.LANGUAGES:
                if self.language_app == lang["code"]:
                    self._load_image(f"calibration{lang['code'][:2]}")
                    break

            if self.camera is None or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(
                    self.camera_index,
                    self.service.get_opencv_capture_backend(),
                )
                if self.camera.isOpened():
                    self._setup_calibration_window()
                    self.camera_timer.start(30)
                else:
                    self.view.msg.critical(
                        self.tr("Não foi possível abrir a câmera.")
                    )
                    self.camera = None

        elif event.key() == Qt.Key_Q:
            self.view.close()

    def _mouse_click_callback(self, event, x, y, flags, param):
        """Store a clicked corner (OpenCV mouse callback).

        Only left clicks count, up to four; after the fourth, the
        success image and message are shown.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.click_calibration_count < 4:
                self.calibration_points[self.click_calibration_count] = [x, y]
                self.click_calibration_count += 1

                if self.click_calibration_count == 4:
                    for lang in Language.LANGUAGES:
                        if self.language_app == lang["code"]:
                            self._load_image(
                                f"calibrationok{lang['code'][:2]}"
                            )
                            break
                    self.view.msg.info(
                        self.tr("Calibração concluída com sucesso!")
                    )

    def _load_image(self, image_name: str):
        """Show a Qt resource image in the instruction label."""
        qimage = PathConfig.image(image_name)
        pixmap = QPixmap(qimage)

        self.view.lbl_image.setScaledContents(True)
        self.view.lbl_image.setPixmap(pixmap)

    def _update_camera_feed(self):
        """Show the next camera frame with skeleton and corners.

        Notes
        -----
        The OpenCV window is recreated if the user closed it. The frame
        is mirrored when ``is_manual_mirror_mode()`` is set. When pose
        detection is enabled, the skeleton is drawn; in VIDEO mode the
        timestamp advances 33 ms per frame (about 30 fps). The clicked
        corners are drawn as blue dots, and the outline is drawn after
        the fourth click.
        """
        from mediapipe.framework.formats import landmark_pb2

        if self.camera is not None and self.camera.isOpened():
            if (
                cv2.getWindowProperty(
                    self.monitor_window, cv2.WND_PROP_VISIBLE
                )
                < 1
            ):
                self._setup_calibration_window()

            ret, frame = self.camera.read()
            if ret:
                if self.service.is_manual_mirror_mode():
                    control_screen = cv2.flip(frame, 1)
                else:
                    control_screen = frame

                if self.service.is_enable_mediapipe_pose():
                    # MediaPipe expects RGB
                    rgb_frame = cv2.cvtColor(control_screen, cv2.COLOR_BGR2RGB)

                    # The Tasks API takes an mp.Image
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB, data=rgb_frame
                    )

                    # IMAGE or VIDEO mode, as configured
                    if (
                        self.service.get_mediapipe_execution_mode()
                        == vision.RunningMode.VIDEO
                    ):
                        self.frame_timestamp += 33  # about 30 fps
                        detection_result = self.pose_detector.detect_for_video(
                            mp_image, self.frame_timestamp
                        )
                    else:
                        detection_result = self.pose_detector.detect(mp_image)

                    if detection_result.pose_landmarks:
                        for pose_landmarks in detection_result.pose_landmarks:
                            # drawing_utils needs the protobuf format
                            pose_landmarks_proto = (
                                landmark_pb2.NormalizedLandmarkList()
                            )
                            pose_landmarks_proto.landmark.extend(
                                [
                                    landmark_pb2.NormalizedLandmark(
                                        x=landmark.x,
                                        y=landmark.y,
                                        z=landmark.z,
                                        visibility=landmark.visibility,
                                        presence=landmark.presence,
                                    )
                                    for landmark in pose_landmarks
                                ]
                            )

                            mp_drawing.draw_landmarks(
                                control_screen,
                                pose_landmarks_proto,
                                mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(
                                    color=(0, 255, 0),
                                    thickness=2,
                                    circle_radius=2,
                                ),
                                mp_drawing.DrawingSpec(
                                    color=(0, 0, 255), thickness=2
                                ),
                            )

                for i in range(4):
                    cv2.circle(
                        control_screen,
                        tuple(self.calibration_points[i]),
                        8,
                        (255, 0, 0),  # blue (BGR)
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
                    )
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

                cv2.imshow(self.monitor_window, control_screen)

            else:
                self.view.msg.critical(
                    self.tr("Falha ao capturar imagem da câmera.")
                )

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
        """Save the clicked corners and show the result."""
        data = self.get_data()
        if self.service.create_calibration_point(data):
            self.view.msg.info(self.tr("Calibração manual salva com sucesso!"))
        else:
            self.view.msg.critical(
                self.tr("Erro ao salvar os pontos da calibração manual.")
            )

    def get_data(self) -> Dict[str, int]:
        """Return the corners as ``CalibrationPoint`` field values.

        Returns
        -------
        dict[str, int]
            ``pointx1``, ``pointy1``... ``pointy4`` from
            ``calibration_points``, in click order.
        """
        # (4, 2) array -> [x1, y1, x2, y2, ...]
        flat_points = self.calibration_points.flatten().tolist()

        return {
            prop: int(val)
            for prop, val in zip(CalibrationPoint.PROPERTIES, flat_points)
        }
