from typing import TYPE_CHECKING, Callable, List, Optional

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

# Local module import
from udescjoinvilletteacontroller import HealthProfessionalListController

from udescjoinvilletteaui import (
    Ui_HealthProfessionalListView,
)  # Assuming generated UI class
from udescjoinvilletteautil import MessageService
from udescjoinvilletteawindow import WindowConfig

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteamodel import HealthProfessional
    from udescjoinvilletteaview import HealthProfessionalEditView


class HealthProfessionalListView(
    QDialog, Ui_HealthProfessionalListView, WindowConfig
):
    def __init__(
        self,
        parent: Optional[QDialog] = None,
        healthprofessional_edit_view_factory: Optional[
            Callable[
                [Optional[QDialog], Optional["HealthProfessional"]],
                "HealthProfessionalEditView",
            ]
        ] = None,
    ) -> None:

        super().__init__(parent)
        # Setup UI interface Ui_PlayerListView
        self.setupUi(self)
        self.msg = MessageService(self)

        # Set up window properties
        self.setup_window(
            self.windowTitle(),
            self.windowIcon(),
            WindowConfig.DECREMENT_SIZE_PERCENT,
            10,
            5,
            parent,
        )

        # Initialize controller
        self.controller = HealthProfessionalListController(
            self, healthprofessional_edit_view_factory
        )

        # Perfect column widths
        self.tbl_health.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.tbl_health.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )

    # =====================================================================
    # High-level methods used by the Controller (required for decoupling)
    # =====================================================================
    def populate_table(
        self, healthprofessionals: List["HealthProfessional"]
    ) -> None:
        """Fill the table with a list of healthprofessionals."""
        self.tbl_health.blockSignals(True)
        self.tbl_health.setRowCount(0)

        for healthprofessional in healthprofessionals:
            row = self.tbl_health.rowCount()
            self.tbl_health.insertRow(row)
            self.tbl_health.setItem(
                row, 0, QTableWidgetItem(str(healthprofessional.id))
            )
            self.tbl_health.setItem(
                row, 1, QTableWidgetItem(healthprofessional.name)
            )

        self.tbl_health.blockSignals(False)

    def clear_details(self) -> None:
        """Clear all fields in the details panel."""
        self.lbl_id_value.setText("")
        self.lbl_name_value.setText("")
        self.lbl_type_value.setText("")

    def display_details(
        self, healthprofessional: Optional["HealthProfessional"]
    ) -> None:
        """Show the selected healthprofessional's
        details in the right panel."""

        if not healthprofessional:
            self.clear_details()
            return

        self.lbl_id_value.setText(str(healthprofessional.id))
        self.lbl_name_value.setText(healthprofessional.name)
        self.lbl_type_value.setText(
            str(
                self.controller.get_healthprofessional_types()[
                    healthprofessional.type
                ]
            )
        )

    def get_selected_id(self) -> Optional[int]:
        """Return the ID of the currently selected pealthprofessional
        or None."""
        items = self.tbl_health.selectedItems()
        if not items:
            return None
        try:
            return int(items[0].text())
        except (ValueError, AttributeError):
            return None

    def select_row_by_id(self, healthprofessional_id: int) -> None:
        """Programmatically select the row with
        the given healthprofessional ID."""
        if healthprofessional_id <= 0:
            return

        self.tbl_health.blockSignals(True)
        for row in range(self.tbl_health.rowCount()):
            item = self.tbl_health.item(row, 0)
            if item and int(item.text()) == healthprofessional_id:
                self.tbl_health.selectRow(row)
                self.tbl_health.scrollToItem(item)
                break
        self.tbl_health.blockSignals(False)
        self.controller.on_table_selection()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override close event to confirm exit.

        Shows a confirmation dialog before allowing the window to close.

        Parameters
        ----------
        event : QCloseEvent
            The close event to accept or ignore.
        """
        if self.msg.question(self.tr("Deseja sair do cadastro?"), None, True):
            event.accept()
        else:
            event.ignore()
