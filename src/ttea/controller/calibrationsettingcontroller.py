"""Controller of the calibration settings window."""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QButtonGroup

from ttea.service import CalibrationSettingService

if TYPE_CHECKING:
    from ttea.view import CalibrationSettingView


class CalibrationSettingController(QObject):
    """Controller of the calibration settings window.

    Parameters
    ----------
    view : CalibrationSettingView
        The settings dialog.
    service : CalibrationSettingService | None, optional
        Settings service. Default is None, which creates a new
        ``CalibrationSettingService``.

    Attributes
    ----------
    view : CalibrationSettingView
        The settings dialog.
    service : CalibrationSettingService
        Settings service.
    calibration_group : QButtonGroup
        Exclusive group of the three "default calibration" check boxes.

    Notes
    -----
    The saved settings are loaded first and the check box group is
    created afterwards, selecting the automatic calibration as default.
    TODO(doc): this overrides the saved default calibration mode; is it
    intended?

    Messages are translated with ``self.tr()``.
    """

    def __init__(
        self,
        view: "CalibrationSettingView",
        service: Optional[CalibrationSettingService] = None,
    ):
        self.view = view
        self.service = service or CalibrationSettingService()
        self._initialize_view()
        self._setup_calibration_group()

    def _setup_calibration_group(self) -> None:
        """Make the default calibration check boxes exclusive."""
        self.calibration_group = QButtonGroup(self.view)
        self.calibration_group.setExclusive(True)

        self.calibration_group.addButton(
            self.view.chk_default_calibration_automatic
        )
        self.calibration_group.addButton(
            self.view.chk_default_calibration_manual
        )
        self.calibration_group.addButton(
            self.view.chk_default_calibration_semiautomatic
        )

        self.view.chk_default_calibration_automatic.setChecked(True)

    def _initialize_view(self):
        """Fill the proportions and load the saved settings."""
        self.list_proportions()
        self._load_saved_settings()

    def _load_saved_settings(self):
        """Show the saved settings, if any, in the view."""
        calibration_setting = self.service.dao.select(0)

        if calibration_setting:
            self.view.set_data(calibration_setting)

    def list_proportions(self) -> None:
        """Fill the ratio combo box with the supported proportions."""
        for text, value in self.service.get_proportions():
            self.view.cbx_ratio.addItem(text, value)

    def handle_ok(self) -> None:
        """Save the settings and close the dialog.

        Notes
        -----
        On success, an information message is shown and the dialog is
        accepted; if the settings are not valid, an error message is
        shown and the dialog stays open.
        """
        data = self.view.get_data()

        calibration = self.service.create_calibration_setting(data)

        if calibration:
            self.view.msg.info(
                self.tr("Configuração de calibração salva com sucesso!")
            )
            self.view.accept()
        else:
            self.view.msg.critical(
                self.tr("Erro ao salvar a configuração de calibração.")
            )

    def handle_cancel(self) -> None:
        """Reject the dialog without saving."""
        self.view.reject()
