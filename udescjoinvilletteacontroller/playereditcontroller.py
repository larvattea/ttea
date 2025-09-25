from datetime import date
from typing import TYPE_CHECKING, Dict, Optional, Union

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import Player
    from udescjoinvilletteaview import PlayerEditView


class PlayerEditController:
    """Controller for managing the PlayerEditView dialog.

    This class handles the logic for editing or creating player data
    within a dialog, including input validation and data retrieval.

    Attributes
    ----------
    view : PlayerEditView
        The dialog view for editing player data.
    player : Player, optional
        The player object being edited, if provided.
    ok_clicked : bool
        Flag indicating if the OK button was clicked.

    Methods
    -------
    __init__(view: PlayerEditView, player: Optional[Player]=None) -> None
        Initialize the controller with view and optional player.
    handle_ok() -> None
        Validate input and accept dialog if valid.
    handle_cancel() -> None
        Close dialog without saving.
    is_input_valid() -> bool
        Validate input fields.
    get_data(self) -> Dict[str, Union[str, date]]
        Return player data from input fields.
    """

    def __init__(
        self, view: "PlayerEditView", player: Optional["Player"] = None
    ) -> None:
        """Initialize the controller with view and optional player.

        Sets up the controller by storing the view and player objects,
        initializing the ok_clicked flag, and populating the view's
        input fields if a player object is provided.

        Parameters
        ----------
        view : PlayerEditView
            The view object associated with the controller.
        player : Player, optional
            The player object to edit, if any (default is None).

        Returns
        -------
        None
        """
        self.view = view
        self.player = player
        self.ok_clicked = False

        # Populate fields if editing
        if player:
            self.view.name_input.setText(player.name)
            birth_date = player.birth_date
            self.view.birth_date_input.setDate(
                QDate(birth_date.year, birth_date.month, birth_date.day)
            )
            self.view.observation_input.setPlainText(player.observation)

    def handle_ok(self) -> None:
        """Validate input and accept dialog if valid.

        Checks if the input fields are valid. If valid, sets the
        ok_clicked flag to True and accepts the dialog. Otherwise,
        displays an error message.

        Returns
        -------
        None
        """
        if self.is_input_valid():
            self.ok_clicked = True
            self.view.accept()

    def handle_cancel(self) -> None:
        """Close dialog without saving.

        Rejects the dialog, closing it without saving any changes.

        Returns
        -------
        None
        """
        self.view.reject()

    def is_input_valid(self) -> bool:
        """Validate input fields.

        Checks if the name field is non-empty. Displays an error message
        if validation fails.

        Returns
        -------
        bool
            True if all inputs are valid, False otherwise.
        """
        error_message = ""

        if not self.view.name_input.text():
            error_message += "Nome é obrigatório!\n"

        if error_message:
            QMessageBox.critical(
                self.view,
                "Dados inválidos",
                "Por favor, corrija os dados inválidos:\n" + error_message,
            )
            return False
        return True

    def get_data(self) -> Dict[str, Union[str, date]]:
        """Return player data from input fields.

        Retrieves the data entered in the dialog's input fields.

        Returns
        -------
        Dict[str, Union[str, date]]
            Dictionary containing player data with keys:
            - name: str, the player's name
            - birth_date: str, the player's birth date
            - observation: str, the player's observation text
        """
        return {
            "name": self.view.name_input.text(),
            "birth_date": self.view.birth_date_input.date().toPython(),
            "observation": self.view.observation_input.toPlainText(),
        }
