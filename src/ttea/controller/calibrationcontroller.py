"""Controller of the calibration window (hardware data and camera)."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtGui import QImage, QPixmap

from ttea.app import AppConfig
from ttea.core import CalibrationMath, CameraVideoThread
from ttea.service import CalibrationService

if TYPE_CHECKING:
    from ttea.view import CalibrationView


class CalibrationController(QObject):
    """Controller of the calibration window.

    Lists cameras, screens and aspect ratios, previews the camera, opens
    the automatic and manual calibrations and saves the hardware data
    (``Calibration``) of the chosen camera and screen.

    Parameters
    ----------
    view : CalibrationView
        The calibration dialog.
    service : CalibrationService | None, optional
        Calibration service. Default is None, which creates a new
        ``CalibrationService``.

    Attributes
    ----------
    view : CalibrationView
        The calibration dialog.
    service : CalibrationService
        Calibration service.
    thread : CameraVideoThread | None
        Camera preview thread, or None when the camera is stopped.

    Notes
    -----
    The combo boxes are filled and the saved camera, screen and
    proportion are selected when the controller is created. User
    messages and button texts are translated with ``self.tr()``.
    """

    def __init__(
        self,
        view: "CalibrationView",
        service: Optional[CalibrationService] = None,
    ):
        self.view = view
        self.service = service or CalibrationService()
        self._initialize_view()
        self.thread = None

    def handle_ok(self) -> None:
        """Save the hardware data and close the dialog.

        Notes
        -----
        The data from ``get_data`` is saved through
        ``create_calibration_hardware``. On success, an information
        message is shown, the dialog is accepted and the camera preview
        is stopped; otherwise an error message is shown.
        """
        data = self.get_data()

        calibration = self.service.create_calibration_hardware(data)

        if calibration:
            self.view.msg.info(
                self.tr(
                    "Dados do hardware do ambiente de calibração cadastrados com sucesso!"
                )
            )
            self.view.accept()
            if self.thread:
                self.thread.stop()

        else:
            self.view.msg.critical(
                self.tr(
                    "Erro ao salvar os dados do hardware do ambiente de calibração."
                )
            )

    def handle_cancel(self) -> None:
        """Stop the camera preview and reject the dialog."""
        if self.thread:
            self.thread.stop()
        self.view.reject()

    def handle_calibrate_auto(self) -> None:
        """Open the automatic calibration dialog."""
        from ttea.factory import ViewFactory

        dialog = ViewFactory.get_app_view_factory().create_automaticcalibration_view(
            self.view
        )
        dialog.exec()

    def handle_calibrate_semi(self) -> None:
        """Show that semiautomatic calibration is not ready."""
        self.view.msg.info(self.tr("Em construção!"))

    def handle_calibrate_manual(self) -> None:
        """Open the manual calibration dialog."""
        from ttea.factory import ViewFactory

        dialog = (
            ViewFactory.get_app_view_factory().create_manualcalibration_view(
                self.view
            )
        )
        dialog.exec()

    def _initialize_view(self):
        """Fill the combo boxes and select the saved values."""
        self.list_proportions()
        self.list_monitors()
        self.list_cameras()
        self._load_saved_settings()

    def _load_saved_settings(self):
        """Select the saved camera, screen and proportion, if any.

        The camera and screen are found by their saved index and the
        proportion by its text; values not found are left unselected.
        """
        calibration = self.service.dao.select(0)

        if calibration:
            if calibration.camera_position is not None:
                index = self.view.cbx_camera.findData(
                    calibration.camera_position
                )

                if index >= 0:
                    self.view.cbx_camera.setCurrentIndex(index)

            if calibration.screen_position is not None:
                index = self.view.cbx_monitor.findData(
                    calibration.screen_position
                )
                if index >= 0:
                    self.view.cbx_monitor.setCurrentIndex(index)

            if calibration.content_proportion:
                index = self.view.cbx_proportion.findText(
                    calibration.content_proportion
                )
                if index >= 0:
                    self.view.cbx_proportion.setCurrentIndex(index)

    def list_cameras(self) -> None:
        """Fill the camera combo box, with the index as data."""
        for i, camera in enumerate(self.service.get_video_inputs()):
            self.view.cbx_camera.addItem(camera.description(), i)

    def list_monitors(self) -> None:
        """Fill the screen combo box (name, with the index as data).

        The name is ``"<manufacturer> - <model>"``, or ``"Monitor <n>
        (<name>)"`` when both are empty.
        """
        for i, monitor in enumerate(self.service.get_screens()):
            manufacturer = monitor.manufacturer()
            model = monitor.model()

            if manufacturer or model:
                descricao = f"{manufacturer} - {model}".strip()
            else:
                descricao = f"Monitor {i+1} ({monitor.name()})"

            self.view.cbx_monitor.addItem(descricao, i)

    def list_proportions(self) -> None:
        """Fill the proportion combo box with the supported ratios."""
        for text, value in self.service.get_proportions():
            self.view.cbx_proportion.addItem(text, value)

    def control_camera(self):
        """Start or stop the camera preview (F5 button).

        Notes
        -----
        While the preview runs, the camera, screen and proportion combo
        boxes are disabled. The ``CameraVideoThread`` is created with
        ``use_low_resolution`` set to ``is_raspberry_pi()``, so the
        configured resolution is applied only on a Raspberry Pi.
        """
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
            self.view.pb_camera.setText(self.tr("Parar Câmera - F5"))
            self.view.pb_camera.setShortcut(self.tr("F5"))
            self.view.cbx_proportion.setEnabled(False)
            self.view.cbx_monitor.setEnabled(False)
            self.view.cbx_camera.setEnabled(False)

    def stop_camera_stream(self):
        """Stop the preview and reset the camera button and image."""
        if self.thread:
            self.thread.stop()
            self.thread = None
        self.view.pb_camera.setText(self.tr("Iniciar Câmera - F5"))
        self.view.pb_camera.setShortcut(self.tr("F5"))
        self.view.lbl_video.clear()
        self.view.lbl_video.setText(self.tr("Câmera Parada"))

    @Slot(str)
    def handle_camera_error(self, message: str):
        """Stop the preview and show a camera error.

        Slot of ``CameraVideoThread.error_signal``.

        Parameters
        ----------
        message : str
            Translated error message.
        """
        self.stop_camera_stream()
        self.view.msg.critical(message)

    @Slot(QImage)
    def update_image(self, qt_img):
        """Show a camera frame, scaled to the video label.

        Slot of ``CameraVideoThread.change_pixmap_signal``.

        Parameters
        ----------
        qt_img : QImage
            Frame to show; the aspect ratio is kept.
        """
        pixmap = QPixmap.fromImage(qt_img)

        # Scale to the label's current size (follows window resizes)
        scaled_pixmap = pixmap.scaled(
            self.view.lbl_video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.view.lbl_video.setPixmap(scaled_pixmap)

    def get_data(self) -> Dict[str, Any]:
        """Build the hardware calibration data from the selection.

        Returns
        -------
        dict[str, Any]
            Values for every ``Calibration`` field.

        Notes
        -----
        The camera resolution and frame rates come from the first video
        format of the camera (0 if it has none). The content area is the
        largest area of the chosen proportion that fits the available
        screen area (``CalibrationMath.calculate_projection_area``). The
        date uses ``AppConfig.get_geral_date_mask()`` and the time
        ``%H:%M:%S``.
        """
        camera_idx = self.view.cbx_camera.currentIndex()
        monitor_idx = self.view.cbx_monitor.currentIndex()
        proportion_text = self.view.cbx_proportion.currentText()

        camera_device = self.service.get_video_inputs()[camera_idx]
        screen = self.service.get_screens()[monitor_idx]
        geometry = self.service.get_geometry_of_screen(monitor_idx)
        available_geo = self.service.get_available_geometry_of_screen(
            monitor_idx
        )

        formats = camera_device.videoFormats()
        best_format = formats[0] if formats else None

        # e.g. "16:9" -> (16, 9)
        ratio_parts = tuple(map(int, proportion_text.split(":")))

        c_width, c_height = CalibrationMath.calculate_projection_area(
            available_geo.width(), available_geo.height(), ratio_parts
        )

        date_mask = AppConfig.get_geral_date_mask()
        current_date = date.today().strftime(date_mask)
        current_hour = datetime.now().strftime("%H:%M:%S")

        data = {
            "camera_description": camera_device.description(),
            "camera_id": camera_device.id().data().decode(),
            "camera_position": camera_idx,
            "camera_width": (
                best_format.resolution().width() if best_format else 0
            ),
            "camera_height": (
                best_format.resolution().height() if best_format else 0
            ),
            "camera_max_fps": (
                int(best_format.maxFrameRate()) if best_format else 0
            ),
            "camera_min_fps": (
                int(best_format.minFrameRate()) if best_format else 0
            ),
            "screen_manufacturer": screen.manufacturer(),
            "screen_model": screen.model(),
            "screen_position": monitor_idx,
            "screen_serial_number": screen.serialNumber(),
            "screen_width": geometry.width(),
            "screen_height": geometry.height(),
            "screen_available_width": available_geo.width(),
            "screen_available_height": available_geo.height(),
            "screen_pos_x": geometry.x(),
            "screen_pos_y": geometry.y(),
            "content_width": c_width,
            "content_height": c_height,
            "content_width_ratio": ratio_parts[0],
            "content_height_ratio": ratio_parts[1],
            "content_proportion": proportion_text,
            "calibration_date": current_date,
            "calibration_hour": current_hour,
        }

        return data
