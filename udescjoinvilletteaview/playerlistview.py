from typing import TYPE_CHECKING, Callable, List, Optional

import qtawesome as qta
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QHeaderView,
                               QTableWidget, QTableWidgetItem)

# Local module import
from udescjoinvilletteaui import Ui_PlayerListView
from udescjoinvilletteautil import MessageService
from udescjoinvilletteawindow import WindowConfig

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteamodel import Player
    from udescjoinvilletteaview import PlayerEditView


class PlayerListView(QDialog, Ui_PlayerListView, WindowConfig):
    """Dialog for displaying and managing the list of players.

    Modal window that shows a searchable table of players with quick actions
    for creating, editing and deleting records. Follows the MVC pattern:
    all business logic and data access are delegated to PlayerListController.

    Attributes
    ----------
    translator : Optional[object]
        Translator object inherited from the parent window (for i18n).
    msg : MessageService
        Helper service used to show info/warning/question dialogs.
    controller : PlayerListController
        Controller that handles all CRUD operations and data flow.
    table : QTableWidget
        Table displaying ID and name of each player.
    new_button : QPushButton
        Button that opens the player creation dialog.
    edit_button : QPushButton
        Button that opens the edit dialog for the selected player.
    delete_button : QPushButton
        Button that removes the selected player after confirmation.
    search_input : QLineEdit
        Line edit used to filter players by ID or name.

    Methods
    -------
    __init__(parent=None, player_edit_view_factory=None)
        Initialise the dialog, UI, controller and signal connections.
    on_new_button_clicked()
        Delegate the "New" action to the controller.
    on_edit_button_clicked()
        Delegate the "Edit" action to the controller.
    on_delete_button_clicked()
        Delegate the "Delete" action to the controller.
    on_search_input_textChanged(text)
        Forward search text changes to the controller for filtering.
    on_table_selection_changed()
        Notify the controller when the table selection changes.
    closeEvent(event)
        Ask for confirmation before closing the dialog.
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
        player_edit_view_factory: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], "PlayerEditView"]
        ] = None,
    ) -> None:
        """Initialise the PlayerListView dialog.

        Parameters
        ----------
        parent : Optional[QDialog], default None
            Parent widget; used for translator and icon inheritance.
        player_edit_view_factory : Optional[Callable], default None
            Factory function that creates PlayerEditView instances.
            Enables dependency injection (useful for testing).
        """
        from udescjoinvilletteacontroller import PlayerListController

        super().__init__(parent)
        self.setModal(True)
        self.translator = (
            parent.translator if hasattr(parent, "translator") else None
        )

        # Setup UI interface Ui_PlayerListView
        self.setupUi(self)
        self.msg = MessageService(self)

        # Set up window properties
        self.setup_window(
            parent.title + " - Jogador",
            parent.windowIcon() if parent else None,
            WindowConfig.DECREMENT_SIZE_PERCENT,
            10,
            5,
            parent,
        )

        # Initialize controller
        self.controller = PlayerListController(self, player_edit_view_factory)

        # Set up table properties not fully handled by .ui file
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        # Set up button icons
        self.new_button.setIcon(qta.icon("fa6s.plus", color="blue"))
        self.edit_button.setIcon(qta.icon("fa6s.pen-to-square", color="black"))
        self.delete_button.setIcon(qta.icon("fa6s.trash", color="red"))

        # Events signals and slots
        self.new_button.clicked.connect(self.on_new_button_clicked)
        self.edit_button.clicked.connect(self.on_edit_button_clicked)
        self.delete_button.clicked.connect(self.on_delete_button_clicked)
        self.search_input.textChanged.connect(self.on_search_input_textChanged)
        self.table.selectionModel().selectionChanged.connect(
            self.on_table_selection_changed
        )

        # Load initial data
        self.controller.load_players()
        # == CONFIGURATION IMPORTANT FOR ROW SELECTION AND SINGLE SELECTION ==
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Perfect column widths
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )

    def on_new_button_clicked(self):
        """Handle the 'New' button click.

        Delegates to the controller to open the player creation dialog.
        """
        self.controller.handle_new_player()

    def on_edit_button_clicked(self):
        """Handle the 'Edit' button click.

        Delegates to the controller to edit the selected player.
        """
        self.controller.handle_edit_player()

    def on_delete_button_clicked(self):
        """Handle the 'Delete' button click.

        Delegates to the controller to remove the selected player after
        confirmation.
        """
        self.controller.delete_player()

    def on_search_input_textChanged(self, text: str):
        """Filter the player list as the user types.

        Parameters
        ----------
        text : str
            Current text in the search input field.
        """
        self.controller.filter_players(text)

    def on_table_selection_changed(self):
        """React to table row selection changes.

        Notifies the controller so it can update the details panel.
        """
        self.controller.on_table_selection()

    # =====================================================================
    # High-level methods used by the Controller (required for decoupling)
    # =====================================================================

    def populate_table(self, players: List["Player"]) -> None:
        """Fill the table with a list of players."""
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for player in players:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(player.id)))
            self.table.setItem(row, 1, QTableWidgetItem(player.name))

        self.table.blockSignals(False)

    def clear_details(self) -> None:
        """Clear all fields in the details panel."""
        self.id_label.setText("")
        self.name_label.setText("")
        self.birth_date_label.setText("")
        self.observation_label.setText("")

    def display_player_details(self, player: Optional["Player"]) -> None:
        """Show the selected player's details in the right panel."""
        from udescjoinvilletteaapp import AppConfig

        if not player:
            self.clear_details()
            return

        self.id_label.setText(str(player.id))
        self.name_label.setText(player.name)
        mask = AppConfig.get_geral_date_mask()
        self.birth_date_label.setText(player.birth_date.strftime(mask))
        self.observation_label.setText(player.observation or "—")

    def get_selected_player_id(self) -> Optional[int]:
        """Return the ID of the currently selected player or None."""
        items = self.table.selectedItems()
        if not items:
            return None
        try:
            return int(items[0].text())
        except (ValueError, AttributeError):
            return None

    def select_row_by_id(self, player_id: int) -> None:
        """Programmatically select the row with the given player ID."""
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == player_id:
                self.table.selectRow(row)
                self.table.scrollToItem(item)
                break
        self.table.blockSignals(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override close event to confirm exit.

        Shows a confirmation dialog before allowing the window to close.

        Parameters
        ----------
        event : QCloseEvent
            The close event to accept or ignore.
        """
        if self.msg.question(self.tr("Deseja sair do cadastro?"), None, False):
            event.accept()
        else:
            event.ignore()
