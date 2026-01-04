from datetime import date
from typing import TYPE_CHECKING, Dict, Optional, Union

from PySide6.QtCore import QDate, QObject

# Local module import
from udescjoinvilletteautil import MessageService, QtDateFormat

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player
    from udescjoinvilletteaview import PlayerEditView


class PlayerEditController(QObject):
    """Controller for the player edit/create dialog.

    Manages the interaction between PlayerEditView and the Player model,
    including field population, input validation, and data extraction.

    Attributes
    ----------
    view : PlayerEditView
        The dialog view containing the input widgets.
    player : Optional[Player]
        Player instance being edited, or None when creating a new player.
    ok_clicked : bool
        True if the dialog was accepted with valid data.
    msg : MessageService
        Service used to display validation/error messages.

    Methods
    -------
    __init__(view, player=None, message_service=None)
        Initialize controller and populate fields if editing.
    handle_ok()
        Validate inputs and accept dialog if valid.
    handle_cancel()
        Reject dialog without saving changes.
    is_input_valid()
        Check required fields and show errors if needed.
    get_data()
        Extract entered data as a dictionary.
    """

    def __init__(
        self,
        view: "PlayerEditView",
        player: Optional["Player"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        """Initialize the controller and prepare the dialog.

        Stores references, sets the ok_clicked flag, and pre-fills the
        form when editing an existing player. Sets current date as default
        for new players.

        Parameters
        ----------
        view : PlayerEditView
            The associated dialog view.
        player : Optional[Player], optional
            Player object to edit; None creates a new player.
        message_service : Optional[MessageService], optional
            Custom message service; defaults to MessageService(view).
        """
        self.view = view
        self.player = player
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)

        # Populate fields if editing
        if player:
            self.view.led_name.setText(player.name)

            birth_date = player.birth_date
            qdate = QDate(birth_date.year, birth_date.month, birth_date.day)
            self.view.ded_birth_date.setDate(qdate)

            self.view.ted_observation.setPlainText(player.observation)
        else:
            self.view.ded_birth_date.setDate(QDate.currentDate())

        self.view.ded_birth_date.setDisplayFormat(QtDateFormat.from_config())

    def handle_ok(self) -> None:
        """Validate input and close dialog with acceptance.

        If validation passes, sets ok_clicked to True and accepts the
        dialog. Otherwise shows a critical message with errors.
        """
        if self.is_input_valid():
            self.ok_clicked = True
            self.view.accept()

    def handle_cancel(self) -> None:
        """Close the dialog without saving changes.

        Rejects the dialog, discarding any entered data.
        """
        self.view.reject()

    def is_input_valid(self) -> bool:
        """Validate required fields.

        Currently checks that the name field is not empty. Shows a
        critical message listing all errors if validation fails.

        Returns
        -------
        bool
            True if all inputs are valid, False otherwise.
        """
        error_message = ""

        if not self.view.led_name.text():
            error_message += self.tr("Nome é obrigatório!\n")

        if error_message:
            self.msg.critical(
                self.tr("Por favor, corrija os dados inválidos:\n")
                + error_message
            )
            return False
        return True

    def get_data(self) -> Dict[str, Union[str, date]]:
        """Extract current form values into a dictionary.

        Returns
        -------
        dict
            Mapping with keys:
            - "name": str from name input
            - "birth_date": date from date editor
            - "observation": str from observation text area
        """
        return {
            "name": self.view.led_name.text(),
            "birth_date": self.view.ded_birth_date.date().toPython(),
            "observation": self.view.ted_observation.toPlainText(),
        }
