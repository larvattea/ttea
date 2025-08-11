from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (QDateEdit, QDialog, QFormLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QTextEdit)

# Local module import
from udescjoinvilletteacontroller import PlayerEditController

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player

from udescjoinvilletteawindow import WindowConfig


class PlayerEditView(QDialog, WindowConfig):
    """Dialog view for editing or adding a player."""

    def __init__(self, parent=None, player: Optional["Player"] = None):
        super().__init__(parent)
        self.setModal(True)  # Make dialog modal
        action = "Editar" if player else "Novo"
        title = parent.parent().get_title()
        self.setup_window(
            f"{title} - {action}",  # title
            parent.windowIcon() if parent else None,  # icon
            WindowConfig.DECREMENT_SIZE_PERCENT,  # status
            40,  # width
            40,  # height
            parent,  # parent
        )

        # Layout
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)

        # Input fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome")

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observação")
        self.observation_input.setMaximumHeight(80)

        # Buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancela")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add to layout
        layout.addRow("Nome:", self.name_input)
        layout.addRow("Data de Nascimento:", self.birth_date_input)
        layout.addRow("Observação:", self.observation_input)
        layout.addRow(button_layout)

        self.setLayout(layout)

        # Initialize controller
        self.controller = PlayerEditController(self, player)

        # Connect buttons to controller
        self.ok_button.clicked.connect(self.controller.handle_ok)
        self.cancel_button.clicked.connect(self.controller.handle_cancel)
