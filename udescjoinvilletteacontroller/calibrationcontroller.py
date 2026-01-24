from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QImage, QPixmap

from udescjoinvilletteaservice import CalibrationService
from udescjoinvilletteacore import CameraVideoThread

if TYPE_CHECKING:
    from udescjoinvilletteaview import CalibrationView


class CalibrationController(QObject):

    def __init__(
        self,
        view: "CalibrationView",
        service: Optional[CalibrationService] = None,
    ):
        self.view = view
        self.service = service or CalibrationService()
        self._initialize_view()
        # Inicialização da Thread
        self.thread = None

    def handle_ok(self) -> None:
        pass

    def handle_cancel(self) -> None:
        self.view.reject()

    def _initialize_view(self):
        self.list_proportions()
        self.list_monitors()
        self.list_cameras()

    def list_cameras(self) -> None:
        for i, camera in enumerate(self.service.get_video_inputs()):
            # Adiciona o nome amigável e guarda o índice como dado extra
            self.view.cbx_camera.addItem(camera.description(), i)

    def list_monitors(self) -> None:
        for i, monitor in enumerate(self.service.get_screens()):
            manufacturer = monitor.manufacturer()
            model = monitor.model()

            if manufacturer or model:
                descricao = f"{manufacturer} - {model}".strip()
            else:
                descricao = f"Monitor {i+1} ({monitor.name()})"

            # Adiciona o nome amigável e guarda o índice como dado extra
            self.view.cbx_monitor.addItem(descricao, i)

    def list_proportions(self) -> None:
        for text, value in self.service.get_proportions():
            self.view.cbx_proportion.addItem(text, value)

    def control_camera(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.view.pb_camera.setText(self.tr("Iniciar Câmera"))
            self.view.lbl_video.clear()
            self.view.lbl_video.setText(self.tr("Câmera Parada"))
        else:
            self.thread = CameraVideoThread(
                int(self.view.cbx_camera.currentIndex())
            )
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.start()
            self.view.pb_camera.setText(self.tr("Parar Câmera"))

    @Slot(QImage)
    def update_image(self, qt_img):
        # self.view.lbl_video.setPixmap(QPixmap.fromImage(qt_img))
        # Criamos o pixmap a partir da cópia enviada pela thread
        pixmap = QPixmap.fromImage(qt_img)

        # Redimensionamos dinamicamente com base no tamanho ATUAL do label na UI
        scaled_pixmap = pixmap.scaled(
            self.view.lbl_video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Aplicamos ao label
        self.view.lbl_video.setPixmap(scaled_pixmap)
