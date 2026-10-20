"""Dialog of the manual calibration."""

from typing import Optional

import cv2
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QDialog

from ttea.controller import ManualCalibrationController
from ttea.model import CalibrationSetting
from ttea.ui import Ui_ManualCalibrationView
from ttea.util import MessageService
from ttea.window import WindowConfig


class ManualCalibrationView(QDialog, Ui_ManualCalibrationView, WindowConfig):
    """Dialog of the manual calibration on the projection screen.

    Shows the instruction images while the user clicks the corners in
    the OpenCV camera window. The logic is in
    ``ManualCalibrationController``.

    Parameters
    ----------
    parent : QDialog | None, optional
        The calibration dialog; its camera and screen selections are
        used (index 0 without a parent). Default is None.

    Attributes
    ----------
    msg : MessageService
        Service used to show dialogs.
    controller : ManualCalibrationController
        Controller of the dialog.

    Notes
    -----
    The window is placed on the projection screen when
    ``is_manual_open_projector()`` is set, otherwise on screen 0. Its
    position is the point returned by the ``QRect`` method named by
    ``get_manual_window_position()`` (e.g. ``"topLeft"``, ``"center"``)
    on the available screen geometry, with ``topLeft`` as fallback.
    ``get_manual_window_open_mode()`` then shows it full screen
    (``FULLSCREEN``) or maximized with the size fixed to the available
    screen area (``MAXIMIZED`` and ``MAXIMIZED_UTIL``).
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

        self.controller = ManualCalibrationController(
            self, camera_index=camera_idx, monitor_index=monitor_idx
        )

        if self.controller.service.is_manual_open_projector():
            screen_geometry = self.controller.get_available_geometry_of_screen(
                monitor_idx
            )
        else:
            monitor_idx = 0
            screen_geometry = self.controller.get_available_geometry_of_screen(
                monitor_idx
            )

        position_name = self.controller.service.get_manual_window_position()

        position_func = getattr(screen_geometry, position_name, None)

        if callable(position_func):
            target_point = position_func()
        else:
            target_point = screen_geometry.topLeft()

        self.move(target_point)

        mode = self.controller.service.get_manual_window_open_mode()

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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Forward key presses to the controller (C starts, Q closes).

        Parameters
        ----------
        event : QKeyEvent
            Key event.
        """
        self.controller.keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask for confirmation and save the points before closing.

        Parameters
        ----------
        event : QCloseEvent
            Close event; accepted only if the user confirms.

        Notes
        -----
        If the camera was opened, it is released, the OpenCV windows are
        closed, the timer is stopped and the clicked points are saved
        (even if fewer than four were clicked).
        """
        if self.msg.question(
            self.tr("Deseja sair da calibração manual?"), None, True
        ):
            if self.controller.camera is not None:
                self.controller.camera.release()
                cv2.destroyAllWindows()
                self.controller.camera_timer.stop()
                self.controller.create_calibration_point()
            event.accept()
        else:
            event.ignore()
