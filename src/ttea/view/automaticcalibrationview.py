"""Dialog of the automatic calibration (ChArUco board)."""

import threading
from typing import Optional

import cv2
from PySide6.QtGui import QCloseEvent, QPainter, QPaintEvent, QShowEvent
from PySide6.QtWidgets import QDialog

from ttea.controller import AutomaticCalibrationController
from ttea.model import CalibrationSetting
from ttea.ui import Ui_AutomaticCalibrationView
from ttea.util import MessageService
from ttea.window import WindowConfig


class AutomaticCalibrationView(
    QDialog, Ui_AutomaticCalibrationView, WindowConfig
):
    """Dialog that shows the ChArUco board on the projection screen.

    The board fills the window; the camera loop of
    ``AutomaticCalibrationController.run_auto_calibration`` runs in a
    separate thread while the window is shown.

    Parameters
    ----------
    parent : QDialog | None, optional
        The calibration dialog; its camera and screen selections are
        used (index 0 without a parent). Default is None.

    Attributes
    ----------
    msg : MessageService
        Service used to show dialogs.
    is_finished : bool
        True when the calibration ended, so closing needs no
        confirmation.
    controller : AutomaticCalibrationController
        Controller of the dialog; its message signals are shown here.
    board_pixmap : QPixmap
        ChArUco board drawn as the window background.

    Notes
    -----
    The window is placed on the projection screen when
    ``is_automatic_open_projector()`` is set, otherwise on screen 0. Its
    position is the point returned by the ``QRect`` method named by
    ``get_automatic_window_position()`` (e.g. ``"topLeft"``,
    ``"center"``) on the available screen geometry, with ``topLeft`` as
    fallback. ``get_automatic_window_open_mode()`` then shows it full
    screen (``FULLSCREEN``) or maximized with the size fixed to the
    available screen area (``MAXIMIZED`` and ``MAXIMIZED_UTIL``).
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.msg = MessageService(self)

        self.setup_window(
            None,
            None,
            WindowConfig.STAY_SIZE,  # status
            0,  # width
            0,  # height
            parent,  # parent
        )

        camera_idx = (
            self.parent().cbx_camera.currentIndex() if self.parent() else 0
        )

        monitor_idx = (
            self.parent().cbx_monitor.currentIndex() if self.parent() else 0
        )

        self.is_finished = False

        self.controller = AutomaticCalibrationController(
            self, camera_index=camera_idx, monitor_index=monitor_idx
        )

        self.controller.msg_info_signal.connect(self.handle_info_then_close)
        self.controller.msg_warning_signal.connect(self.msg.warning)
        self.controller.msg_critical_signal.connect(self.msg.critical)

        if self.controller.service.is_automatic_open_projector():
            screen_geometry = self.controller.get_available_geometry_of_screen(
                monitor_idx
            )
        else:
            monitor_idx = 0
            screen_geometry = self.controller.get_available_geometry_of_screen(
                monitor_idx
            )

        position_name = self.controller.service.get_automatic_window_position()

        position_func = getattr(screen_geometry, position_name, None)

        if callable(position_func):
            target_point = position_func()
        else:
            target_point = screen_geometry.topLeft()

        self.move(target_point)

        mode = self.controller.service.get_automatic_window_open_mode()

        if mode == CalibrationSetting.FULLSCREEN:
            self.showFullScreen()
        elif mode == CalibrationSetting.MAXIMIZED:
            self.showMaximized()
            self.setFixedSize(
                screen_geometry.width(),
                screen_geometry.height(),
            )
        elif mode == CalibrationSetting.MAXIMIZED_UTIL:
            screen_geometry = self.controller.get_available_geometry_of_screen(
                monitor_idx
            )
            self.showMaximized()
            self.setFixedSize(
                screen_geometry.width(),
                screen_geometry.height(),
            )

        self.board_pixmap = self.controller.generate_board_pixmap()

    def handle_info_then_close(self, message: str) -> None:
        """Show an information message; close if calibration ended.

        Slot of ``msg_info_signal``.

        Parameters
        ----------
        message : str
            Translated message.

        Notes
        -----
        The message box is modal, so the window closes only after the
        user clicks OK. It closes when the message is the translated
        "saved" or "closing without saving" text.
        """
        self.msg.info(message)

        if not self.isVisible():
            return

        msg_sucesso = self.tr("Calibração automática salva com sucesso!")
        msg_sem_salvar = self.tr("Fechando sem salvar.")

        if message in (msg_sucesso, msg_sem_salvar):
            self.is_finished = True
            self.close()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw the board over the whole window.

        Parameters
        ----------
        event : QPaintEvent
            Paint event.
        """
        super().paintEvent(event)
        if hasattr(self, "board_pixmap") and not self.board_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.board_pixmap)

    def showEvent(self, event: QShowEvent) -> None:
        """Start the calibration loop in a daemon thread when shown.

        Running the OpenCV loop in a thread keeps the Qt window
        responsive.

        Parameters
        ----------
        event : QShowEvent
            Show event.
        """
        super().showEvent(event)

        calib_thread = threading.Thread(
            target=self.controller.run_auto_calibration, daemon=True
        )
        calib_thread.start()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close the window, asking for confirmation if not finished.

        Parameters
        ----------
        event : QCloseEvent
            Close event; accepted when the calibration ended or the user
            confirms.
        """
        if self.is_finished:
            if self.controller.camera is not None:
                self.controller.camera.release()
                cv2.destroyAllWindows()
            event.accept()
            return

        if self.msg.question(
            self.tr("Deseja sair da calibração automática?"), None, True
        ):
            if self.controller.camera is not None:
                self.controller.camera.release()
                cv2.destroyAllWindows()
            event.accept()
        else:
            event.ignore()
