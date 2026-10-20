"""Controller of the player edit/create dialog."""

from datetime import date
from typing import TYPE_CHECKING, Dict, Optional, Union

from PySide6.QtCore import QDate, QObject

from ttea.service import PlayerService
from ttea.util import MessageService, QtDateFormat

# Type-checking-only imports, to avoid circular imports at run time
if TYPE_CHECKING:
    from ttea.model import Player
    from ttea.view import PlayerEditView


class PlayerEditController(QObject):
    """Controller for the player edit/create dialog.

    Fills the form of ``PlayerEditView``, validates the input through
    the service and returns the entered data to the list controller.

    Parameters
    ----------
    view : PlayerEditView
        The dialog view.
    player : Player | None, optional
        Player to edit; None creates a new one. Default is None.
    message_service : MessageService | None, optional
        Service used to show messages. Default is None, which creates
        ``MessageService(view)``.

    Attributes
    ----------
    view : PlayerEditView
        The dialog view.
    service : PlayerService
        Service used to validate the data.
    player : Player | None
        Player being edited, or None when creating one.
    ok_clicked : bool
        True after the dialog was accepted with valid data.
    msg : MessageService
        Service used to show messages.

    Methods
    -------
    handle_ok()
        Validate the input and accept the dialog if valid.
    handle_cancel()
        Reject the dialog without saving.
    get_data()
        Return the entered data as a dictionary.

    Notes
    -----
    The OK and Cancel buttons are connected to ``handle_ok`` and
    ``handle_cancel``. Saving is done by the list controller, which
    reads ``get_data()`` after the dialog is accepted.
    """

    def __init__(
        self,
        view: "PlayerEditView",
        player: Optional["Player"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        self.view = view
        self.service = PlayerService()
        self.player = player
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)
        self._initialize_view()

        self.view.pb_ok.clicked.connect(self.handle_ok)
        self.view.pb_cancel.clicked.connect(self.handle_cancel)

    def _initialize_view(self):
        """Fill the form, with the edited player if any.

        The birth date defaults to today for a new player, and the date
        format comes from ``QtDateFormat.from_config()``.
        """
        if self.player:
            self.view.led_name.setText(self.player.name)
            self.view.ded_birth_date.setDate(
                QtDateFormat.to_qdate(self.player.birth_date)
            )
            self.view.ted_observation.setPlainText(self.player.observation)
        else:
            self.view.ded_birth_date.setDate(QDate.currentDate())

        self.view.ded_birth_date.setDisplayFormat(QtDateFormat.from_config())

    def handle_ok(self) -> None:
        """Validate the input and accept the dialog if it is valid.

        Notes
        -----
        The data is checked by ``service.validate_data``. On errors, a
        critical message lists them and the dialog stays open; otherwise
        ``ok_clicked`` becomes True and the dialog is accepted. The
        message header is translated with ``self.tr()``.
        """
        data = self.get_data()
        errors = self.service.validate_data(data)

        if errors:
            self.msg.critical(
                self.tr("Por favor, corrija os dados inválidos:\n")
                + "".join(errors)
            )
            return

        self.ok_clicked = True
        self.view.accept()

    def handle_cancel(self) -> None:
        """Reject the dialog, discarding the entered data."""
        self.view.reject()

    def get_data(self) -> Dict[str, Union[str, date]]:
        """Return the form values as a dictionary.

        Returns
        -------
        dict[str, Any]
            Keys ``"id"`` (the edited player's ID, or 0 for a new one),
            ``"name"``, ``"birth_date"`` (``datetime.date``) and
            ``"observation"``.
        """
        return {
            "id": (
                self.player.id if self.player and self.player.id != 0 else 0
            ),
            "name": self.view.led_name.text(),
            "birth_date": self.view.ded_birth_date.date().toPython(),
            "observation": self.view.ted_observation.toPlainText(),
        }
