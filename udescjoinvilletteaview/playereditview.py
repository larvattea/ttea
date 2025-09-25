from typing import TYPE_CHECKING, Optional

import qtawesome as qta
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QDateEdit, QDialog, QDialogButtonBox,
                               QFormLayout, QLineEdit, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget)

# Local module import
from udescjoinvilletteacontroller import PlayerEditController

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteamodel import Player

from udescjoinvilletteawindow import WindowConfig


class PlayerEditView(QDialog, WindowConfig):
    """
    Dialog view for editing or adding a player.

    This class creates a modal dialog for editing an existing player or adding
    a new one. It includes input fields for the player's name, birth date, and
    observations within a tab, along with OK and Cancel buttons in a QDialogButtonBox
    aligned at the bottom.

    Parameters
    ----------
    parent : Optional[QWidget], optional
        The parent widget for the dialog, by default None.
    player : Optional[Player], optional
        The player object to edit, by default None (for new players).

    Attributes
    ----------
    translator : Optional[QObject]
        Translator object for handling translations, inherited from parent.
    name_input : QLineEdit
        Input field for the player's name.
    birth_date_input : QDateEdit
        Input field for the player's birth date with a calendar popup.
    observation_input : QTextEdit
        Input field for additional observations about the player.
    button_box : QDialogButtonBox
        Standard button box with OK and Cancel buttons.
    controller : PlayerEditController
        Controller for handling dialog actions.

    Methods
    -------
    __init__(parent=None, player=None)
        Initialize the PlayerEditView dialog.
    """

    def __init__(self, parent=None, player: Optional["Player"] = None):
        """
        Initialize the PlayerEditView dialog.

        Parameters
        ----------
        parent : Optional[QWidget], optional
            The parent widget for the dialog, by default None.
        player : Optional[Player], optional
            The player object to edit, by default None (for new players).

        Notes
        -----
        Sets up a modal dialog with input fields for name, birth date, and
        observations grouped in a tab, and OK and Cancel buttons in a
        QDialogButtonBox aligned at the bottom. The dialog title is dynamically
        set based on whether a player is being edited or added. The controller
        is initialized to handle button actions.
        """
        super().__init__(parent)
        self.setModal(True)  # Make dialog modal
        self.translator = (
            parent.translator if hasattr(parent, "translator") else None
        )
        action = "Jogador - Editar" if player else "Jogador - Novo"
        title = parent.parent().get_title()
        self.setup_window(
            f"{title} - {action}",  # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            40,  # width
            40,  # height
            parent,  # parent
        )

        # Main layout
        main_layout = QVBoxLayout()

        # Tab widget for input fields
        tab_widget = QTabWidget()
        details_tab = QWidget()
        details_layout = QFormLayout()
        details_layout.setLabelAlignment(Qt.AlignRight)

        # Input fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome")

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observação")
        self.observation_input.setMaximumHeight(80)

        # Add to details layout
        details_layout.addRow("Nome:", self.name_input)
        details_layout.addRow("Data de Nascimento:", self.birth_date_input)
        details_layout.addRow("Observação:", self.observation_input)

        details_tab.setLayout(details_layout)
        tab_widget.addTab(details_tab, "Dados")

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        icon_ok = qta.icon("fa6s.check", color="green")
        self.button_box.button(QDialogButtonBox.Ok).setText("OK")
        self.button_box.button(QDialogButtonBox.Ok).setIcon(icon_ok)
        self.button_box.button(QDialogButtonBox.Ok).setToolTip(
            "Gravar operação corrente"
        )

        icon_cancel = qta.icon("fa6s.xmark", color="red")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")
        self.button_box.button(QDialogButtonBox.Cancel).setIcon(icon_cancel)
        self.button_box.button(QDialogButtonBox.Cancel).setToolTip(
            "Cancelar operação corrente"
        )

        # Add to main layout
        main_layout.addWidget(tab_widget)  # Tab without explicit stretch
        main_layout.addWidget(self.button_box)  # Buttons at the bottom

        self.setLayout(main_layout)

        # Initialize controller
        self.controller = PlayerEditController(self, player)

        # Connect buttons to controller
        self.button_box.accepted.connect(self.controller.handle_ok)
        self.button_box.rejected.connect(self.controller.handle_cancel)
