"""Plain camera capture thread for Qt views.

Reads frames from an OpenCV camera in a ``QThread`` and emits them
as ``QImage`` objects, with no pose detection or telemetry (see
``CameraVideoThread`` for that).
"""

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from ttea.service import CalibrationService


class CameraVideo(QThread):
    """Capture camera frames in a thread and emit them as images.

    Parameters
    ----------
    camera_index : int
        OpenCV index of the camera.
    use_low_resolution : bool, optional
        If True, keep the camera's default resolution; otherwise set
        the width and height configured in ``CalibrationService``.
        Default is False.

    Attributes
    ----------
    frame_ready : Signal(QImage)
        Emitted for each captured frame, as an RGB888 image that a
        ``QLabel`` can display directly.
    camera_index : int
        OpenCV index of the camera.
    use_low_resolution : bool
        Whether the configured resolution is skipped.
    running : bool
        Loop flag; set to True by ``run`` and to False by ``stop``.
    cap : cv2.VideoCapture | None
        The open capture device, or None before ``run``.
    service : CalibrationService
        Source of the OpenCV settings.

    Notes
    -----
    The camera is opened with the backend from
    ``get_opencv_capture_backend()``; the Windows and non-Windows
    branches are currently identical.

    The emitted ``QImage`` wraps the frame buffer without copying it.

    ``run`` emits ``self.error_signal`` when the camera cannot be
    opened, but this class defines no such signal, so that case
    raises ``AttributeError``. TODO(doc): add
    ``error_signal = Signal(str)`` as in ``CameraVideoThread``?

    The error message uses ``self.tr()`` (runtime Qt translation).
    """

    frame_ready = Signal(QImage)

    def __init__(self, camera_index: int, use_low_resolution: bool = False):
        super().__init__()
        self.camera_index = camera_index
        self.use_low_resolution = use_low_resolution
        self.running = False
        self.cap = None
        self.service = CalibrationService()

    def run(self):
        """Capture frames until stopped or the camera fails.

        Runs in the thread when ``start()`` is called. Each frame is
        converted from BGR (OpenCV) to RGB and emitted through
        ``frame_ready``. The loop ends when ``stop`` is called or a
        frame cannot be read (e.g. camera disconnected); the camera is
        then released.
        """
        if self.service.is_windows():
            self.cap = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )
        else:
            self.cap = cv2.VideoCapture(
                self.camera_index, self.service.get_opencv_capture_backend()
            )

        if not self.cap.isOpened():
            self.error_signal.emit(self.tr("Não foi possível abrir a câmera."))
            return

        if not self.use_low_resolution:
            self.cap.set(
                cv2.CAP_PROP_FRAME_WIDTH, self.service.get_opencv_width()
            )
            self.cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                self.service.get_opencv_height(),
            )

        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Qt expects RGB, while OpenCV delivers BGR.
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            height, width, channels = frame_rgb.shape
            bytes_per_line = channels * width

            q_image = QImage(
                frame_rgb.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            )

            self.frame_ready.emit(q_image)

        if self.cap and self.cap.isOpened():
            self.cap.release()

    def stop(self):
        """Stop the capture loop and wait for the thread to finish."""
        self.running = False
        self.wait()
