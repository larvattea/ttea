from typing import TYPE_CHECKING, Callable, Optional

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QTableWidget, QVBoxLayout, QWidget)

from udescjoinvilletteagames.kartea.controller import \
    PlayerKarteaConfigListController
from udescjoinvilletteawindow import WindowConfig

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig
    from udescjoinvilletteagames.kartea.view import PlayerKarteaConfigEditView


class PlayerKarteaConfigListView(QDialog, WindowConfig):
    """View class for the PlayerKarteaConfig management UI.

    This class provides a dialog for managing player Kartea configurations, including
    searching, viewing, and editing configuration details.

    Attributes
    ----------
    translator : Optional[QObject]
        Translator object for handling UI translations.
    controller : PlayerKarteaConfigListController
        Controller handling the business logic for player Kartea configuration management.
    search_label : QLabel
        Label for the search input field.
    search_input : QLineEdit
        Input field for searching configurations by player name or ID.
    table : QTableWidget
        Table displaying player ID and name.
    id_label : QLabel
        Label displaying the selected configuration's player ID.
    name_label : QLabel
        Label displaying the selected configuration's player name.
    current_phase_label : QLabel
        Label displaying the selected configuration's current phase.
    current_level_label : QLabel
        Label displaying the selected configuration's current level.
    level_time_label : QLabel
        Label displaying the selected configuration's level time.
    new_button : QPushButton
        Button to create a new configuration record.
    edit_button : QPushButton
        Button to edit the selected configuration record.
    delete_button : QPushButton
        Button to delete the selected configuration record.

    Methods
    -------
    __init__(parent=None, player_kartea_config_edit_view_factory=None) -> None
        Initializes the PlayerKarteaConfigListView dialog.
    closeEvent(event: QCloseEvent) -> None
        Handles the dialog close event with a confirmation prompt.
    """

    def __init__(
        self,
        parent: Optional[QDialog] = None,
        player_kartea_config_edit_view_factory: Optional[
            Callable[
                [Optional[QDialog], Optional["PlayerKarteaConfig"]],
                "PlayerKarteaConfigEditView",
            ]
        ] = None,
    ) -> None:
        """Initialize the PlayerKarteaConfigListView dialog.

        Sets up the UI components, including search, table, and details
        panel, and connects them to the controller.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            Parent widget for the dialog, by default None.
        player_kartea_config_edit_view_factory : Optional[Callable], optional
            Factory function to create PlayerKarteaConfigEditView instances,
            by default None.

        Notes
        -----
        - The dialog is set to modal to prevent interaction with the
          parent window.
        - The window size is decremented by a percentage defined in
          WindowConfig.
        - Initial configuration data is loaded via the controller.
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
        self.controller = PlayerKarteaConfigListController(
            self, player_kartea_config_edit_view_factory
        )
        # Create main layout
        layout = QHBoxLayout(self)
        # Left side: Search and Table
        left_layout = QVBoxLayout()
        # Search field
        search_layout = QHBoxLayout()
        self.search_label = QLabel("Pesquisar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome ou ID do jogador")
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)

        # Table setup
        self.table = QTableWidget()
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

        # Right side: Configuration details and buttons
        details_widget = QWidget()
        details_widget.setFixedWidth(400)
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Detalhes"))
        # Details labels
        self.id_label = QLabel("ID: ")
        self.name_label = QLabel("Nome: ")
        self.current_phase_label = QLabel("Fase Atual: ")
        self.current_level_label = QLabel("Nível Atual: ")
        self.level_time_label = QLabel("Tempo do Nível: ")

        # Add labels to details layout
        details_grid = QGridLayout()
        details_grid.addWidget(QLabel("ID:"), 0, 0, alignment=Qt.AlignLeft)
        details_grid.addWidget(self.id_label, 0, 1, alignment=Qt.AlignLeft)
        details_grid.addWidget(QLabel("Nome:"), 1, 0, alignment=Qt.AlignLeft)
        details_grid.addWidget(self.name_label, 1, 1, alignment=Qt.AlignLeft)
        details_grid.addWidget(
            QLabel("Fase Atual:"), 2, 0, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            self.current_phase_label, 2, 1, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            QLabel("Nível Atual:"), 3, 0, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            self.current_level_label, 3, 1, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            QLabel("Tempo do Nível:"), 4, 0, alignment=Qt.AlignLeft
        )
        details_grid.addWidget(
            self.level_time_label, 4, 1, alignment=Qt.AlignLeft
        )
        details_layout.addLayout(details_grid)

        # Buttons
        self.new_button = QPushButton(
            qta.icon("fa6s.plus", color="blue"), "Novo"
        )
        self.new_button.setToolTip("Criar um novo registro")

        self.edit_button = QPushButton(
            qta.icon("fa6s.pen-to-square", color="black"), "Editar"
        )
        self.edit_button.setToolTip("Editar o registro selecionado")
        self.delete_button = QPushButton(
            qta.icon("fa6s.trash", color="red"), "Excluir"
        )
        self.delete_button.setToolTip("Excluir o registro selecionado")

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        # Add buttons below details
        details_layout.addStretch()  # Push content to top
        details_layout.addLayout(button_layout)
        details_widget.setLayout(details_layout)

        # Add to main layout
        layout.addLayout(left_layout)
        layout.addWidget(details_widget)

        # Connect buttons and search to controller
        self.new_button.clicked.connect(self.controller.handle_new_config)
        self.edit_button.clicked.connect(self.controller.handle_edit_config)
        self.delete_button.clicked.connect(self.controller.delete_config)
        self.search_input.textChanged.connect(self.controller.filter_configs)

        # Load initial data
        self.controller.load_configs()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the dialog close event with a confirmation prompt.

        Displays a confirmation dialog asking the user if they want to
        exit the configuration management dialog.

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
        msg_box.setText(self.tr("Deseja sair do cadastro de configurações?"))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # Translate the buttons
        msg_box.button(QMessageBox.Yes).setText(self.tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.tr("Não"))

        # Execute dialog and handle response
        if msg_box.exec() == QMessageBox.Yes:
            event.accept()  # Close the window
        else:
            event.ignore()  # Keep the window open
