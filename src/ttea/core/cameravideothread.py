"""Camera thread with pose detection and telemetry overlay.

Captures frames from an OpenCV camera, optionally enhances them,
runs MediaPipe pose detection, draws the skeleton and a telemetry
panel, and emits the result to the Qt interface.
"""

import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import pose as mp_pose
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QImage

from ttea.service import CalibrationService


class CameraVideoThread(QThread, QObject):
    """Capture, analyze and annotate camera frames in a thread.

    Parameters
    ----------
    camera_index : int
        OpenCV index of the camera.
    use_low_resolution : bool, optional
        If True, set the width and height configured in
        ``CalibrationService`` on the camera. Default is False.

    Attributes
    ----------
    change_pixmap_signal : Signal(QImage)
        Emitted for each processed frame with an RGB888 copy of the
        annotated image.
    error_signal : Signal(str)
        Emitted with a translated message when the camera cannot be
        opened or a frame cannot be read.
    camera_index : int
        OpenCV index of the camera.
    running : bool
        Loop flag; True on creation, set to False by ``stop``.
    mp_manager : MediaPipeManager
        Pose detector.
    use_low_resolution : bool
        Whether the configured resolution is applied.
    filter : MediaPipeFilter
        Frame enhancement and landmark smoothing.
    service : CalibrationService
        Source of the camera, filter, pose and telemetry settings.
    last_timestamp_ms : int
        Timestamp of the last frame sent to MediaPipe.

    Notes
    -----
    The configured resolution is applied only when
    ``use_low_resolution`` is True, the opposite of ``CameraVideo``.
    TODO(doc): is this inversion intended?

    User-facing texts (error messages and telemetry labels) use
    ``self.tr()`` (runtime Qt translation).
    """

    change_pixmap_signal = Signal(QImage)
    error_signal = Signal(str)

    def __init__(self, camera_index: int, use_low_resolution: bool = False):
        from ttea.core import MediaPipeFilter, MediaPipeManager

        super().__init__()
        self.camera_index = camera_index
        self.running = True
        self.mp_manager = MediaPipeManager()
        self.use_low_resolution = use_low_resolution
        self.filter = MediaPipeFilter()
        self.service = CalibrationService()
        self.last_timestamp_ms = 0

    def _convert_to_proto(self, landmarks):
        """Convert Task API landmarks to a ``NormalizedLandmarkList``.

        ``mp_drawing.draw_landmarks`` expects the protobuf format;
        missing ``visibility`` or ``presence`` values default to 0.0.
        """
        landmark_subset = landmark_pb2.NormalizedLandmarkList()
        for l in landmarks:
            landmark_subset.landmark.add(
                x=l.x,
                y=l.y,
                z=l.z,
                visibility=getattr(l, "visibility", 0.0),
                presence=getattr(l, "presence", 0.0),
            )
        return landmark_subset

    def run(self):
        """Capture and process frames until stopped or the camera fails.

        Runs in the thread when ``start()`` is called.

        Notes
        -----
        For each frame:

        1. The mean brightness (V channel in HSV) is measured.
        2. ``MediaPipeFilter.apply_enhancements`` runs if
           ``is_filter_enable_filter()``.
        3. If ``is_enable_mediapipe_pose()``, the pose is detected and
           smoothed, and the skeleton is drawn (green landmarks, red
           connections). Timestamps are forced to increase by at least
           1 ms, as MediaPipe VIDEO mode requires.
        4. If ``is_telemetry_enable_panel()``, the panel shows FPS
           (green at 15 or more, red below), brightness and the feet
           tracking confidence: the mean ``visibility`` of landmarks 31
           and 32, green above 0.5, red otherwise. The confidence is
           shown as a 0-1 value although the label says "%".
        5. The frame is emitted through ``change_pixmap_signal``.

        When a frame cannot be read, ``error_signal`` is emitted and the
        loop ends. The camera is released on exit.
        """
        if self.service.is_windows():
            cap = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )
        else:
            cap = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )

        if not cap.isOpened():
            self.error_signal.emit(self.tr("Não foi possível abrir a câmera."))
            return

        prev_time = 0

        if self.use_low_resolution:
            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                self.service.get_opencv_width(),
            )
            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                self.service.get_opencv_height(),
            )

        while self.running:
            ret, frame = cap.read()

            if ret:
                # Brightness is measured to debug full-light scenes.
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                avg_brightness = np.mean(hsv[:, :, 2])

                if self.service.is_filter_enable_filter():
                    frame = self.filter.apply_enhancements(frame)

                curr_time = time.time()
                fps = (
                    1 / (curr_time - prev_time)
                    if (curr_time - prev_time) > 0
                    else 0
                )
                prev_time = curr_time

                if self.service.is_enable_mediapipe_pose():
                    timestamp_ms = int(time.time() * 1000)
                    if timestamp_ms <= self.last_timestamp_ms:
                        timestamp_ms = self.last_timestamp_ms + 1
                    self.last_timestamp_ms = timestamp_ms

                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB, data=rgb_frame
                    )

                    result = self.mp_manager.detect_for_video(
                        mp_image, timestamp_ms
                    )

                    if result.pose_landmarks:
                        result.pose_landmarks = self.filter.smooth_landmarks(
                            result.pose_landmarks
                        )

                        for landmarks in result.pose_landmarks:
                            mp_drawing.draw_landmarks(
                                frame,
                                self._convert_to_proto(landmarks),
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

                            # 31 and 32: left and right foot tips.
                            conf_esq = landmarks[31].visibility
                            conf_dir = landmarks[32].visibility
                            c_color = (
                                (0, 255, 0)
                                if (conf_esq + conf_dir) / 2 > 0.5
                                else (0, 0, 255)
                            )

                            if self.service.is_telemetry_enable_panel():
                                text = self.tr(
                                    "Rastreio dos Pés (%): {:.2f}"
                                ).format((conf_esq + conf_dir) / 2)
                                frame = self.put_text_unicode(
                                    frame,
                                    text,
                                    position=(
                                        15,
                                        50,
                                    ),  # Y is lower: PIL uses text top
                                    font_size=22,
                                    color=c_color,
                                )

                if self.service.is_telemetry_enable_panel():
                    fps_color = (0, 255, 0) if fps >= 15 else (0, 0, 255)
                    cv2.putText(
                        frame,
                        self.tr("FPS: {}").format(int(fps)),
                        (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        fps_color,
                        2,
                    )
                    cv2.putText(
                        frame,
                        self.tr("Brilho: {}").format(int(avg_brightness)),
                        (15, 105),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 0),
                        2,
                    )

                display_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = display_rgb.shape
                qt_img = QImage(
                    display_rgb.data, w, h, ch * w, QImage.Format_RGB888
                )
                self.change_pixmap_signal.emit(qt_img.copy())
            else:
                self.error_signal.emit(
                    self.tr(
                        "Erro ao capturar imagem da câmera. Dispositivo desconectado.\nVerifique a conexão do cabo e/ou a instalação da câmera.\nFeche a janela e tente novamente."
                    )
                )
                break

        cap.release()

    def stop(self):
        """Stop the capture loop and wait for the thread to finish."""
        self.running = False
        self.wait()

    def put_text_unicode(
        self,
        img,
        text,
        position,
        font_size=20,
        color=(255, 255, 255),
        font_path=None,
    ):
        """Draw Unicode text on an OpenCV image using PIL.

        OpenCV's ``putText`` cannot render accented characters, so the
        image is converted to PIL, drawn and converted back.

        Parameters
        ----------
        img : numpy.ndarray
            BGR image from OpenCV.
        text : str
            Text to draw.
        position : tuple[int, int]
            ``(x, y)`` of the top-left corner of the text.
        font_size : int, optional
            Font size in points. Default is 20.
        color : tuple[int, int, int], optional
            Text color in BGR. Default is white.
        font_path : str | None, optional
            TrueType font file. Default is None, which tries
            ``DejaVuSans.ttf`` (Linux), then ``arial.ttf`` (Windows),
            then PIL's default font.

        Returns
        -------
        numpy.ndarray
            New BGR image with the text drawn.
        """
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        if font_path is None:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)  # Linux
            except Exception:
                try:
                    font = ImageFont.truetype(
                        "arial.ttf", font_size
                    )  # Windows
                except Exception:
                    font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, font_size)

        draw.text(position, text, font=font, fill=color[::-1])  # BGR → RGB

        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
