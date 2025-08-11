from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QTableWidget, QVBoxLayout, QWidget)

from udescjoinvilletteacontroller import PlayerListController
from udescjoinvilletteawindow import WindowConfig

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player
    from udescjoinvilletteaview import PlayerEditView


class PlayerListView(QDialog, WindowConfig):
    """View class for the Player management UI.

    This class provides a dialog for managing players, including
    searching, viewing, and editing player details.

    Attributes
    ----------
    translator : Optional[QObject]
        Translator object for handling UI translations.
    controller : PlayerListController
        Controller handling the business logic for player management.
    search_label : QLabel
        Label for the search input field.
    search_input : QLineEdit
        Input field for searching players by name or ID.
    table : QTableWidget
        Table displaying player ID and name.
    id_label : QLabel
        Label displaying the selected player's ID.
    name_label : QLabel
        Label displaying the selected player's name.
    birth_date_label : QLabel
        Label displaying the selected player's birth date.
    observation_label : QLabel
        Label displaying the selected player's observation.
    new_button : QPushButton
        Button to create a new player record.
    edit_button : QPushButton
        Button to edit the selected player record.
    delete_button : QPushButton
        Button to delete the selected player record.

    Methods
    -------
    __init__(parent=None, player_edit_view_factory=None) -> None
        Initializes the PlayerListView dialog.
    closeEvent(event: QCloseEvent) -> None
        Handles the dialog close event with a confirmation prompt.
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
        player_edit_view_factory: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], "PlayerEditView"]
        ] = None,
    ) -> None:
        """Initialize the PlayerListView dialog.

        Sets up the UI components, including search, table, and details
        panel, and connects them to the controller.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            Parent widget for the dialog, by default None.
        player_edit_view_factory : Optional[Callable], optional
            Factory function to create PlayerEditView instances,
            by default None.

        Notes
        -----
        - The dialog is set to modal to prevent interaction with the
          parent window.
        - The window size is decremented by a percentage defined in
          WindowConfig.
        - Initial player data is loaded via the controller.
        """
        super().__init__(parent)
        # Make dialog modal
        self.setModal(True)
        self.translator = (
            parent.translator if hasattr(parent, "translator") else None
        )
        self.setup_window(
            parent.title,  # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            10,  # width
            5,  # height
            parent,  # parent
        )
        # Initialize controller
        self.controller = PlayerListController(self, player_edit_view_factory)
        # Create main layout
        layout = QHBoxLayout(self)
        # Left side: Search and Table
        left_layout = QVBoxLayout()
        # Search field
        search_layout = QHBoxLayout()
        self.search_label = QLabel("Pesquisar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome ou ID")
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)

        # Table setup
        self.table = QTableWidget()
        # Only ID and Name
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Nome"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.selectionModel().selectionChanged.connect(
            self.controller.on_table_selection
        )

        # Add to left layout
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.table)

        # Right side: Player details and buttons
        details_widget = QWidget()
        # Fixed width for details panel
        details_widget.setFixedWidth(325)
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Detalhes"))
        # Details labels
        self.id_label = QLabel("ID: ")
        self.name_label = QLabel("Nome: ")
        self.birth_date_label = QLabel("Data de Nascimento: ")
        self.observation_label = QLabel("Observação: ")

        # Add labels to details layout
        details_grid = QGridLayout()
        details_grid.addWidget(QLabel("ID:"), 0, 0, alignment=Qt.AlignLeft)
        details_grid.addWidget(self.id_label, 0, 1, alignment=Qt.AlignLeft)
        details_grid.addWidget(QLabel("Nome:"), 1, 0, alignment=Qt.AlignLeft)
        details_grid.addWidget(self.name_label, 1, 1, alignment=Qt.AlignLeft)
        details_grid.addWidget(
            QLabel("Data de Nascimento:"), 2, 0, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            self.birth_date_label, 2, 1, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            QLabel("Observação:"), 3, 0, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            self.observation_label, 3, 1, alignment=Qt.AlignLeft
        )
        details_layout.addLayout(details_grid)

        # Buttons
        self.new_button = QPushButton("Novo")
        self.new_button.setToolTip("Criar um novo registro")
        self.edit_button = QPushButton("Editar")
        self.edit_button.setToolTip("Editar o registro selecionado")
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setToolTip("Excluir o registro selecionado")

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        # Add buttons below details
        # Push content to top
        details_layout.addStretch()
        details_layout.addLayout(button_layout)
        details_widget.setLayout(details_layout)

        # Add to main layout
        layout.addLayout(left_layout)
        layout.addWidget(details_widget)

        # Connect buttons and search to controller
        self.new_button.clicked.connect(self.controller.handle_new_player)
        self.edit_button.clicked.connect(self.controller.handle_edit_player)
        self.delete_button.clicked.connect(self.controller.delete_player)
        self.search_input.textChanged.connect(self.controller.filter_players)

        # Load initial data
        self.controller.load_players()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the dialog close event with a confirmation prompt.

        Displays a confirmation dialog asking the user if they want to
        exit the player management dialog.

        Parameters
        ----------
        event : QCloseEvent
            The close event triggered when attempting to close the dialog.

        Notes
        -----
        - If the user selects "Yes," the dialog closes.
        - If the user selects "No," the close event is ignored, keeping
          the dialog open.
        - The dialog uses the parent's window title and icon for
          consistency.
        """
        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.parent().windowIcon())
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.parent().windowTitle())
        # Use self.tr
        msg_box.setText(self.tr("Deseja sair do cadastro?"))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # Translate the buttons
        # Use self.tr
        msg_box.button(QMessageBox.Yes).setText(self.tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.tr("Não"))

        # Execute dialog and handle response
        if msg_box.exec() == QMessageBox.Yes:
            event.accept()  # Close the window
        else:
            event.ignore()  # Keep the window open
