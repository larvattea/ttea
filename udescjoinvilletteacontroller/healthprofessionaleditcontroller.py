from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from PySide6.QtCore import QObject

# Local module import
from udescjoinvilletteaservice import HealthProfessionalService
from udescjoinvilletteautil import MessageService

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import HealthProfessional
    from udescjoinvilletteaview import HealthProfessionalEditView


class HealthProfessionalEditController(QObject):
    """Controller for the healthprofessional edit/create dialog.

    Manages the interaction between PlayerEditView and the Player model,
    including field population, input validation, and data extraction.

    Attributes
    ----------
    view : PlayerEditView
        The dialog view containing the input widgets.
    healthprofessional : Optional[InstitutionFacility]
        Player instance being edited, or None when creating
        a new healthprofessional.
    ok_clicked : bool
        True if the dialog was accepted with valid data.
    msg : MessageService
        Service used to display validation/error messages.

    Methods
    -------
    __init__(view, healthprofessional=None, message_service=None)
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
        view: "HealthProfessionalEditView",
        healthprofessional: Optional["HealthProfessional"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        """Initialize the controller and prepare the dialog.

        Stores references, sets the ok_clicked flag, and pre-fills the
        form when editing an existing healthprofessional.
        Sets current date as default for new healthprofessionals.

        Parameters
        ----------
        view : HealthProfessionalEditView
            The associated dialog view.
        healthprofessional : Optional[HealthProfessional], optional
            HealthProfessional object to edit;
            None creates a new healthprofessional.
        message_service : Optional[MessageService], optional
            Custom message service; defaults to MessageService(view).
        """
        self.view = view
        self.service = HealthProfessionalService()
        self.healthprofessional = healthprofessional
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)
        self._initialize_view()

    def _initialize_view(self):
        self.list_types()
        self.list_institutions()

        # Populate fields if editing
        if self.healthprofessional:
            self.view.led_name.setText(self.healthprofessional.name)

            index = self.view.cbx_type.findData(self.healthprofessional.type)
            self.view.cbx_type.setCurrentIndex(index)

            index = self.view.cbx_institution.findData(
                int(self.healthprofessional.institutionfacility)
            )
            self.view.cbx_institution.setCurrentIndex(index)
        else:
            self.view.cbx_type.setCurrentIndex(0)
            self.view.cbx_institution.setCurrentIndex(0)

    def list_types(self) -> None:
        self.view.cbx_type.clear()

        types = self.service.get_healthprofessional_types()
        for type_id, type_name in types.items():
            self.view.cbx_type.addItem(type_name, type_id)

    def list_institutions(self) -> None:
        self.view.cbx_institution.clear()

        institutions = self.service.get_all_institutionfacilities()
        for institution in institutions:
            self.view.cbx_institution.addItem(institution.name, institution.id)

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
        institution_name = self.view.cbx_institution.currentText()
        institution = next(
            (
                i
                for i in self.service.get_all_institutionfacilities()
                if i.name == institution_name
            ),
            None,
        )

        return {
            "id": (
                self.healthprofessional.id
                if self.healthprofessional and self.healthprofessional.id != 0
                else 0
            ),
            "name": self.view.led_name.text(),
            "type": self.view.cbx_type.currentData(),
            "institutionfacility": institution,  # institution.id if institution else None,
        }
