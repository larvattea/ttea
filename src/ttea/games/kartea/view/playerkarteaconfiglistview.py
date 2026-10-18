"""View (Qt dialog) of the player Kartea configuration list."""

from typing import TYPE_CHECKING

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

from ttea.games.kartea.ui import (
    Ui_PlayerKarteaConfigListView,
)
from ttea.util import MessageService
from ttea.window import WindowConfig

# Imported only for type checking, to avoid circular imports at
# runtime.
if TYPE_CHECKING:
    from ttea.games.kartea.controller import PlayerKarteaConfigListController
    from ttea.games.kartea.model import PlayerKarteaConfig


class PlayerKarteaConfigListView(
    QDialog, Ui_PlayerKarteaConfigListView, WindowConfig
):
    """Dialog that lists and manages PlayerKarteaConfig records.

    Modal window that shows a searchable table of configs with quick
    actions for creating, editing and deleting records. Follows the MVC
    pattern: all business logic and data access are delegated to
    PlayerKarteaConfigListController. The view does not create its
    controller: KarteaViewFactory creates both and calls
    ``bind(controller)``.

    Parameters
    ----------
    parent : QDialog | None, optional
        Parent widget; used for translator and icon inheritance.

    Attributes
    ----------
    msg : MessageService
        Helper service used to show info/warning/question dialogs.
    controller : PlayerKarteaConfigListController | None
        Controller that handles all CRUD operations and data flow; None
        until ``bind`` is called.
    tbl_config : QTableWidget
        Table displaying ID and name of each player config.
    pb_new : QPushButton
        Button that opens the config creation dialog.
    pb_edit : QPushButton
        Button that opens the edit dialog for the selected config.
    pb_delete : QPushButton
        Button that removes the selected config after confirmation.
    led_search : QLineEdit
        Line edit used to filter configs by ID or name.

    Methods
    -------
    bind(controller)
        Connect signals to the controller and load the initial data.
    get_search_text()
        Return the current search text.
    populate_table(configs)
        Fill the table with configs.
    clear_details() / display_config_details(config)
        Clear or fill the details panel.
    get_selected_player_id() / select_row_by_id(player_id)
        Read or set the selected row.
    closeEvent(event)
        Ask for confirmation before closing the dialog.

    Notes
    -----
    The widgets come from the generated Ui_PlayerKarteaConfigListView
    (``setupUi``). User texts are translated with ``self.tr()`` (i18n).
    """

    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.controller: PlayerKarteaConfigListController | None = None

        self.setupUi(self)
        self.msg = MessageService(self)

        self.setup_window(
            self.windowTitle(),
            self.windowIcon(),
            WindowConfig.DECREMENT_SIZE_PERCENT,
            10,
            5,
            parent,
        )

        # Column widths: ID fits its content, name stretches
        self.tbl_config.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.tbl_config.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )

    def bind(self, controller: "PlayerKarteaConfigListController") -> None:
        """Connect the signals to the controller and load the data.

        Called by KarteaViewFactory.

        Parameters
        ----------
        controller : PlayerKarteaConfigListController
            Controller of this view.
        """
        self.controller = controller

        # Signals and slots
        self.pb_new.clicked.connect(self.controller.handle_new_config)
        self.pb_edit.clicked.connect(self.controller.handle_edit_config)
        self.pb_delete.clicked.connect(self.controller.delete_config)
        self.led_search.textChanged.connect(self.controller.filter_configs)
        self.tbl_config.selectionModel().selectionChanged.connect(
            self.controller.on_table_selection
        )

        self.controller.load_configs()

    # ==================================================================
    # High-level methods used by the Controller (required for
    # decoupling)
    # ==================================================================

    def get_search_text(self) -> str:
        """Return the current text of the search field.

        Returns
        -------
        str
            Text typed in ``led_search``.
        """
        return self.led_search.text()

    def populate_table(self, configs: list["PlayerKarteaConfig"]) -> None:
        """Fill the table with a list of configs.

        Parameters
        ----------
        configs : list[PlayerKarteaConfig]
            Configs shown as rows (player ID and name).

        Notes
        -----
        Table signals are blocked while filling, so the selection
        handler is not triggered.
        """
        self.tbl_config.blockSignals(True)
        self.tbl_config.setRowCount(0)

        for config in configs:
            row = self.tbl_config.rowCount()
            self.tbl_config.insertRow(row)
            self.tbl_config.setItem(
                row, 0, QTableWidgetItem(str(config.player.id))
            )
            self.tbl_config.setItem(
                row, 1, QTableWidgetItem(config.player.name)
            )

        self.tbl_config.blockSignals(False)

    def clear_details(self) -> None:
        """Clear all fields in the details panel."""
        self.lbl_id_value.setText("")
        self.lbl_name_value.setText("")
        self.lbl_phase_value.setText("")
        self.lbl_level_value.setText("")
        self.lbl_time_value.setText("")

    def display_config_details(
        self, config: "PlayerKarteaConfig | None"
    ) -> None:
        """Show the selected config's details in the right panel.

        Parameters
        ----------
        config : PlayerKarteaConfig | None
            Config to show (ID, name, phase, level and level time); None
            clears the panel.
        """
        if not config:
            self.clear_details()
            return

        self.lbl_id_value.setText(str(config.player.id))
        self.lbl_name_value.setText(config.player.name)
        self.lbl_phase_value.setText(
            str(config.phase.id) if config.phase else ""
        )
        self.lbl_level_value.setText(
            str(config.level.id) if config.level else ""
        )
        self.lbl_time_value.setText(str(config.level_time))

    def get_selected_player_id(self) -> int | None:
        """Return the player ID of the selected row.

        Returns
        -------
        int | None
            The ID in the first selected cell, or None if nothing is
            selected or the text is not a number.
        """
        items = self.tbl_config.selectedItems()
        if not items:
            return None
        try:
            return int(items[0].text())
        except (ValueError, AttributeError):
            return None

    def select_row_by_id(self, player_id: int) -> None:
        """Programmatically select the row with the given player ID.

        Parameters
        ----------
        player_id : int
            Player ID to select; the table scrolls to it. Signals are
            blocked while selecting.
        """
        self.tbl_config.blockSignals(True)
        for row in range(self.tbl_config.rowCount()):
            item = self.tbl_config.item(row, 0)
            if item and int(item.text()) == player_id:
                self.tbl_config.selectRow(row)
                self.tbl_config.scrollToItem(item)
                break
        self.tbl_config.blockSignals(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Confirm before closing the dialog.

        Shows a confirmation question before allowing the window to
        close.

        Parameters
        ----------
        event : QCloseEvent
            The close event to accept or ignore.
        """
        if self.msg.question(self.tr("Deseja sair do cadastro?"), None, True):
            event.accept()
        else:
            event.ignore()
