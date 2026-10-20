"""Controller of the institution facility edit/create dialog."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from PySide6.QtCore import QObject

from ttea.service import InstitutionFacilityService
from ttea.util import MessageService

# Type-checking-only imports, to avoid circular imports at run time
if TYPE_CHECKING:
    from ttea.model import InstitutionFacility
    from ttea.view import InstitutionFacilityEditView


class InstitutionFacilityEditController(QObject):
    """Controller for the institution facility edit/create dialog.

    Fills the form of ``InstitutionFacilityEditView``, validates the
    input through the service and returns the entered data to the list
    controller.

    Parameters
    ----------
    view : InstitutionFacilityEditView
        The dialog view.
    institutionfacility : InstitutionFacility | None, optional
        Institution facility to edit; None creates a new one. Default is
        None.
    message_service : MessageService | None, optional
        Service used to show messages. Default is None, which creates
        ``MessageService(view)``.

    Attributes
    ----------
    view : InstitutionFacilityEditView
        The dialog view.
    service : InstitutionFacilityService
        Service used to validate the data.
    institutionfacility : InstitutionFacility | None
        Institution facility being edited, or None when creating one.
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
    list_types()
        Fill the type combo box.

    Notes
    -----
    The OK and Cancel buttons are connected to ``handle_ok`` and
    ``handle_cancel``. Saving is done by the list controller, which
    reads ``get_data()`` after the dialog is accepted.
    """

    def __init__(
        self,
        view: "InstitutionFacilityEditView",
        institutionfacility: Optional["InstitutionFacility"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        self.view = view
        self.service = InstitutionFacilityService()
        self.institutionfacility = institutionfacility
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)
        self._initialize_view()

        self.view.pb_ok.clicked.connect(self.handle_ok)
        self.view.pb_cancel.clicked.connect(self.handle_cancel)

    def _initialize_view(self):
        """Fill the form, with the edited institution facility if any.

        The type combo box is filled first; for a new facility, its
        first item is selected.
        """
        self.list_types()

        if self.institutionfacility:
            self.view.led_name.setText(self.institutionfacility.name)

            index = self.view.cbx_type.findData(self.institutionfacility.type)
            self.view.cbx_type.setCurrentIndex(index)

            self.view.led_address.setText(self.institutionfacility.address)
            self.view.led_phone.setText(self.institutionfacility.phone)
            self.view.led_email.setText(self.institutionfacility.email)
            self.view.led_website.setText(self.institutionfacility.website)
            self.view.led_social_network.setText(
                self.institutionfacility.social_network
            )
        else:
            self.view.cbx_type.setCurrentIndex(0)

    def list_types(self) -> None:
        """Fill the type combo box with the translated types."""
        self.view.cbx_type.clear()

        types = self.service.get_institutionfacility_types()
        for type_id, type_name in types.items():
            self.view.cbx_type.addItem(type_name, type_id)

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

    def get_data(self) -> Dict[str, Union[str, Any]]:
        """Return the form values as a dictionary.

        Returns
        -------
        dict[str, Any]
            Keys ``"id"`` (the edited facility's ID, or 0 for a new
            one), ``"name"``, ``"type"`` (type code), ``"address"``,
            ``"phone"``, ``"email"``, ``"website"`` and
            ``"social_network"``.
        """
        return {
            "id": (
                self.institutionfacility.id
                if self.institutionfacility
                and self.institutionfacility.id != 0
                else 0
            ),
            "name": self.view.led_name.text(),
            "type": self.view.cbx_type.currentData(),
            "address": self.view.led_address.text(),
            "phone": self.view.led_phone.text(),
            "email": self.view.led_email.text(),
            "website": self.view.led_website.text(),
            "social_network": self.view.led_social_network.text(),
        }
