from datetime import date
from typing import TYPE_CHECKING, Any, Dict, Optional

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtGui import QImage, QPixmap

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteacore import CalibrationMath, CameraVideoThread
from udescjoinvilletteaservice import CalibrationService

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
        data = self.get_data()

        # O Service cria o objeto, valida e salva via DAO
        calibration = self.service.create_update_calibration(data)

        if calibration:
            self.view.msg.info(self.tr("Calibração cadastrada com sucesso!"))
            self.view.accept()
        else:
            self.view.msg.critical(self.tr("Erro salvar a calibração."))

    def handle_cancel(self) -> None:
        if self.thread:
            self.thread.stop()
        self.view.reject()

    def _initialize_view(self):
        self.list_proportions()
        self.list_monitors()
        self.list_cameras()
        self._load_saved_settings()

    def _load_saved_settings(self):
        calibration = self.service.dao.select(0)

        if calibration:
            # 1. Posiciona a Câmera pela posição salva
            if calibration.camera_position is not None:
                index = self.view.cbx_camera.findData(
                    calibration.camera_position
                )

                if index >= 0:
                    self.view.cbx_camera.setCurrentIndex(index)

            # 2. Posiciona o Monitor pela posição salva
            if calibration.screen_position is not None:
                index = self.view.cbx_monitor.findData(
                    calibration.screen_position
                )
                if index >= 0:
                    self.view.cbx_monitor.setCurrentIndex(index)

            # 3. Posiciona a Proporção pelo conteúdo salvo
            if calibration.content_proportion:
                index = self.view.cbx_proportion.findText(
                    calibration.content_proportion
                )
                if index >= 0:
                    self.view.cbx_proportion.setCurrentIndex(index)

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
            self.stop_camera_stream()
            self.view.cbx_proportion.setEnabled(True)
            self.view.cbx_monitor.setEnabled(True)
            self.view.cbx_camera.setEnabled(True)
        else:
            limit_resolution_raspberry = self.service.is_raspberry_pi()
            self.thread = CameraVideoThread(
                int(self.view.cbx_camera.currentIndex()),
                limit_resolution_raspberry,
            )
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.error_signal.connect(self.handle_camera_error)
            self.thread.start()
            self.view.pb_camera.setText(self.tr("Parar Câmera"))
            self.view.cbx_proportion.setEnabled(False)
            self.view.cbx_monitor.setEnabled(False)
            self.view.cbx_camera.setEnabled(False)

    def stop_camera_stream(self):
        """Limpa o estado da UI e garante a parada da thread."""
        if self.thread:
            self.thread.stop()
        self.view.pb_camera.setText(self.tr("Iniciar Câmera"))
        self.view.lbl_video.clear()
        self.view.lbl_video.setText(self.tr("Câmera Parada"))

    @Slot(str)
    def handle_camera_error(self, message: str):
        """Exibe mensagem de erro e reseta a UI."""
        self.stop_camera_stream()
        self.view.msg.critical(message)  # Usa o MessageService da View

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

    def get_data(self) -> Dict[str, Any]:
        # 1. Recuperamos os índices selecionados na UI
        # e busca-se os objetos de hardware via Service
        camera_idx = self.view.cbx_camera.currentIndex()
        monitor_idx = self.view.cbx_monitor.currentIndex()
        proportion_text = self.view.cbx_proportion.currentText()

        camera_device = self.service.get_video_inputs()[camera_idx]
        screen = self.service.get_screens()[monitor_idx]
        geometry = self.service.get_geometry_of_screen(monitor_idx)
        available_geo = self.service.get_available_geometry_of_screen(
            monitor_idx
        )

        # 2. Resolução e FPS da Câmera
        formatos = camera_device.videoFormats()
        melhor_formato = formatos[0] if formatos else None

        # 3. Cálculo da Área de Projeção (Math)
        # Extrai os números da string "16:9" por exemplo -> (16, 9)
        ratio_parts = tuple(map(int, proportion_text.split(":")))

        c_width, c_height = CalibrationMath.calculate_projection_area(
            available_geo.width(), available_geo.height(), ratio_parts
        )

        # 4. Mapeamento do Dicionário
        date_mask = AppConfig.get_geral_date_mask() or "%d/%m/%Y"
        current_date = date.today().strftime(date_mask)

        data = {
            "camera_description": camera_device.description(),
            "camera_id": camera_device.id().data().decode(),
            "camera_position": camera_idx,
            "camera_width": (
                melhor_formato.resolution().width() if melhor_formato else 0
            ),
            "camera_height": (
                melhor_formato.resolution().height() if melhor_formato else 0
            ),
            "camera_max_fps": (
                int(melhor_formato.maxFrameRate()) if melhor_formato else 0
            ),
            "camera_min_fps": (
                int(melhor_formato.minFrameRate()) if melhor_formato else 0
            ),
            "screen_manufacturer": screen.manufacturer(),
            "screen_model": screen.model(),
            "screen_position": monitor_idx,
            "screen_serial_number": screen.serialNumber(),
            "screen_width": geometry.width(),
            "screen_height": geometry.height(),
            "screen_available_width": available_geo.width(),
            "screen_available_height": available_geo.height(),
            "content_width": c_width,
            "content_height": c_height,
            "content_width_ratio": ratio_parts[0],
            "content_height_ratio": ratio_parts[1],
            "content_proportion": proportion_text,
            "calibration_date": current_date,
        }

        return data
