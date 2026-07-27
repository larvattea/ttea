from typing import Optional

import cv2
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QDialog

# Local module import
from controller import ManualCalibrationController
from ui import Ui_GameCalibrationView
from util import MessageService
from window import WindowConfig


class ManualCalibrationView(QDialog, Ui_GameCalibrationView, WindowConfig):

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

        # Initialize controller
        self.controller = ManualCalibrationController(
            self, camera_index=camera_idx, monitor_index=monitor_idx
        )

        self.setFixedSize(
            self.controller.get_available_geometry_of_screen().width(),
            self.controller.get_available_geometry_of_screen().height(),
        )
        self.move(self.controller.get_available_geometry_of_screen().topLeft())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Encaminha o evento de teclado para o controller"""
        self.controller.keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override close event to confirm exit.

        Shows a confirmation dialog before allowing the window to close.

        Parameters
        ----------
        event : QCloseEvent
            The close event to accept or ignore.
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
