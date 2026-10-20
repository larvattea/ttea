"""Calibration settings dialog."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDoubleSpinBox,
                               QRadioButton, QSpinBox)

from ttea.controller import CalibrationSettingController
from ttea.ui import Ui_CalibrationSettingView
from ttea.util import MessageService
from ttea.window import WindowConfig

if TYPE_CHECKING:
    from ttea.model import CalibrationSetting


class CalibrationSettingView(QDialog, Ui_CalibrationSettingView, WindowConfig):
    """Modal dialog with the calibration settings.

    Each settings widget has the Qt property ``dataclass_property`` with
    the name of its ``CalibrationSetting`` field; ``get_data`` and
    ``set_data`` use it to read and fill the form. The logic is in
    ``CalibrationSettingController``.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent widget. Default is None.

    Attributes
    ----------
    msg : MessageService
        Service used to show dialogs.
    controller : CalibrationSettingController
        Controller of the dialog.

    Notes
    -----
    The window is fixed at 5% wider and 75% taller than the parent. The
    camera groups are enabled by the custom camera check box and the
    filter group by the filter check box.
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
        self.controller = CalibrationSettingController(self)

        self.pb_ok.clicked.connect(self.controller.handle_ok)
        self.pb_cancel.clicked.connect(self.controller.handle_cancel)

        self.chk_custom_camera.toggled.connect(self.grp_camera_info.setEnabled)
        self.chk_custom_camera.toggled.connect(self.grp_fps.setEnabled)
        self.chk_enable_filter.toggled.connect(self.grp_filter.setEnabled)

        self.grp_camera_info.setEnabled(self.chk_custom_camera.isChecked())
        self.cbx_ratio.setEnabled(self.chk_custom_camera.isChecked())
        self.grp_fps.setEnabled(self.chk_custom_camera.isChecked())
        self.grp_filter.setEnabled(self.chk_enable_filter.isChecked())

    def get_data(self) -> Dict[str, Any]:
        """Read the settings from the widgets.

        Returns
        -------
        dict[str, Any]
            Values by ``dataclass_property`` name.

        Notes
        -----
        Check boxes give 1 or 0, spin boxes their value and combo boxes
        their current text. For radio buttons, only the checked one sets
        the value: its ``dataclass_property_value`` property, or its
        text.
        """
        from PySide6.QtWidgets import QWidget

        data: Dict[str, Any] = {}

        widgets_to_scan = self.findChildren(QWidget)

        for widget in widgets_to_scan:  # self.findChildren(widgets_to_scan):

            # Name set as a dynamic property in Qt Designer
            prop_name = widget.property("dataclass_property")
            if not prop_name:
                continue

            if isinstance(widget, QCheckBox):
                data[prop_name] = 1 if widget.isChecked() else 0
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                data[prop_name] = widget.value()
            elif isinstance(widget, QComboBox):
                data[prop_name] = widget.currentText()
            elif isinstance(widget, QRadioButton):
                if widget.isChecked():
                    prop_value = widget.property("dataclass_property_value")

                    if prop_value is None:
                        prop_value = widget.text()
                    data[prop_name] = prop_value

        return data

    def set_data(
        self, data: Union[Dict[str, Any], "CalibrationSetting"]
    ) -> None:
        """Fill the widgets with saved settings.

        Parameters
        ----------
        data : dict[str, Any] | CalibrationSetting
            Settings by field name, or a ``CalibrationSetting`` (read
            with ``get_data``). Other types are ignored.

        Notes
        -----
        Empty or None values are skipped. Combo boxes select the item
        with the same text, and a radio button is checked when its
        ``dataclass_property_value`` (or text) equals the value.
        """
        from PySide6.QtWidgets import QWidget

        if hasattr(data, "get_data"):
            data_dict = data.get_data()[0]
        elif isinstance(data, dict):
            data_dict = data
        else:
            return

        for widget in self.findChildren(QWidget):
            prop_name = widget.property("dataclass_property")
            if not prop_name or prop_name not in data_dict:
                continue

            value = data_dict[prop_name]

            if value is None or str(value).strip() == "":
                continue

            if isinstance(widget, QCheckBox):
                # Accepts 1/0 or a bool
                widget.setChecked(bool(int(value)))

            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(
                    float(value)
                    if isinstance(widget, QDoubleSpinBox)
                    else int(value)
                )

            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)

            elif isinstance(widget, QRadioButton):
                prop_value = widget.property("dataclass_property_value")

                target_value = (
                    str(prop_value)
                    if prop_value is not None
                    else widget.text()
                )
                # if widget.text() == str(value):
                if target_value == str(value):
                    widget.setChecked(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ask for confirmation before closing.

        Parameters
        ----------
        event : QCloseEvent
            Close event; accepted only if the user confirms.
        """
        if self.msg.question(
            self.tr("Deseja sair da configuração de calibração?"), None, True
        ):
            event.accept()
        else:
            event.ignore()
