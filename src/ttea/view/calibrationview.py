"""Calibration dialog: hardware data, camera preview and modes."""

from typing import Optional

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog

from ttea.controller import CalibrationController
from ttea.ui import Ui_CalibrationView
from ttea.util import MessageService
from ttea.window import WindowConfig


class CalibrationView(QDialog, Ui_CalibrationView, WindowConfig):
    """Modal dialog of the calibration environment.

    Lets the user choose the camera, screen and proportion, preview the
    camera and open the automatic or manual calibration. The logic is in
    ``CalibrationController``.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent widget. Default is None.

    Attributes
    ----------
    msg : MessageService
        Service used to show dialogs.
    controller : CalibrationController
        Controller of the dialog.

    Notes
    -----
    The window is fixed at 5% wider and 75% taller than the parent. The
    semiautomatic calibration button is hidden.
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
            WindowConfig.INCREMENT_SIZE_PERCENT,  # status
            5,  # width
            75,  # height
            parent,  # parent
        )
        self.controller = CalibrationController(self)
        self.pb_camera.clicked.connect(self.controller.control_camera)

        self.pb_calibrate_auto.clicked.connect(
            self.controller.handle_calibrate_auto
        )
        self.pb_calibrate_semi.clicked.connect(
            self.controller.handle_calibrate_semi
        )
        self.pb_calibrate_semi.setVisible(False)

        self.pb_calibrate_manual.clicked.connect(
            self.controller.handle_calibrate_manual
        )

        self.pb_ok.clicked.connect(self.controller.handle_ok)
        self.pb_cancel.clicked.connect(self.controller.handle_cancel)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask for confirmation and stop the camera before closing.

        Parameters
        ----------
        event : QCloseEvent
            Close event; accepted only if the user confirms (translated
            question, "No" by default).
        """
        if self.msg.question(
            self.tr("Deseja sair da calibração?"), None, True
        ):
            if self.controller.thread:
                self.controller.thread.stop()
            event.accept()
        else:
            event.ignore()
