import cv2
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage


class CameraVideoThread(QThread):
    # Sinal que envia a imagem processada para a interface
    change_pixmap_signal = Signal(QImage)

    # CAMERA_VIDEO_THREAD_WIDTH = 640
    # CAMERA_VIDEO_THREAD_HEIGHT = 480

    def __init__(self, camera_index: int):
        super().__init__()
        self._run_flag = True
        self.camera_index = camera_index

    def run(self):
        # CAP_DSHOW for windows systema
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                # Converte de BGR (OpenCV) para RGB (Qt)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(
                    rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                # p = convert_to_qt_format.scaled(
                #    CameraVideoThread.CAMERA_VIDEO_THREAD_WIDTH,
                #    CameraVideoThread.CAMERA_VIDEO_THREAD_HEIGHT,
                #    Qt.KeepAspectRatio,
                # )
                # self.change_pixmap_signal.emit(p)
                # Envia a imagem original para o Controller tratar
                self.change_pixmap_signal.emit(convert_to_qt_format.copy())

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()
