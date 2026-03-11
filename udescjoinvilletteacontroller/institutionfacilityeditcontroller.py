from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from PySide6.QtCore import QObject

# Local module import
from udescjoinvilletteaservice import InstitutionFacilityService
from udescjoinvilletteautil import MessageService

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import InstitutionFacility
    from udescjoinvilletteaview import InstitutionFacilityEditView


class InstitutionFacilityEditController(QObject):
    """Controller for the institutionfacility edit/create dialog.

    Manages the interaction between PlayerEditView and the Player model,
    including field population, input validation, and data extraction.

    Attributes
    ----------
    view : PlayerEditView
        The dialog view containing the input widgets.
    institutionfacility : Optional[InstitutionFacility]
        Player instance being edited, or None when creating
        a new institutionfacility.
    ok_clicked : bool
        True if the dialog was accepted with valid data.
    msg : MessageService
        Service used to display validation/error messages.

    Methods
    -------
    __init__(view, institutionfacility=None, message_service=None)
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
        view: "InstitutionFacilityEditView",
        institutionfacility: Optional["InstitutionFacility"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        """Initialize the controller and prepare the dialog.

        Stores references, sets the ok_clicked flag, and pre-fills the
        form when editing an existing institutionfacility. Sets current date as default
        for new institutionfacilities.

        Parameters
        ----------
        view : InstitutionFacilityEditView
            The associated dialog view.
        institutionfacility : Optional[Player], optional
            Player object to edit; None creates a new institutionfacility.
        message_service : Optional[MessageService], optional
            Custom message service; defaults to MessageService(view).
        """
        self.view = view
        self.service = InstitutionFacilityService()
        self.institutionfacility = institutionfacility
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)
        self._initialize_view()

        # Populate fields if editing
        if institutionfacility:
            self.view.led_name.setText(institutionfacility.name)

            index = self.view.cbx_type.findData(institutionfacility.type)
            self.view.cbx_type.setCurrentIndex(index)

            self.view.led_address.setText(institutionfacility.address)
            self.view.led_phone.setText(institutionfacility.phone)
            self.view.led_email.setText(institutionfacility.email)
            self.view.led_website.setText(institutionfacility.website)
            self.view.led_social_network.setText(
                institutionfacility.social_network
            )
        else:
            self.view.cbx_type.setCurrentIndex(0)

    def _initialize_view(self):
        self.list_types()

    def list_types(self) -> None:
        self.view.cbx_type.clear()

        types = self.service.get_institutionfacility_types()
        for type_id, type_name in types.items():
            self.view.cbx_type.addItem(type_name, type_id)

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

        if self.view.cbx_type.currentIndex() == 0:
            error_message += self.tr("Tipo é obrigatório!\n")

        if error_message:
            self.msg.critical(
                self.tr("Por favor, corrija os dados inválidos:\n")
                + error_message
            )
            return False
        return True

    def get_data(self) -> Dict[str, Union[str, Any]]:
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
