"""Controller of the professional edit/create dialog."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from PySide6.QtCore import QObject

from ttea.service import ProfessionalService
from ttea.util import MessageService

# Type-checking-only imports, to avoid circular imports at run time
if TYPE_CHECKING:
    from ttea.model import Professional
    from ttea.view import ProfessionalEditView


class ProfessionalEditController(QObject):
    """Controller for the professional edit/create dialog.

    Fills the form of ``ProfessionalEditView``, validates the input
    through the service and returns the entered data to the list
    controller.

    Parameters
    ----------
    view : ProfessionalEditView
        The dialog view.
    professional : Professional | None, optional
        Professional to edit; None creates a new one. Default is None.
    message_service : MessageService | None, optional
        Service used to show messages. Default is None, which creates
        ``MessageService(view)``.

    Attributes
    ----------
    view : ProfessionalEditView
        The dialog view.
    service : ProfessionalService
        Service used to validate the data.
    professional : Professional | None
        Professional being edited, or None when creating one.
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
    list_institutions()
        Fill the institution combo box.

    Notes
    -----
    The OK and Cancel buttons are connected to ``handle_ok`` and
    ``handle_cancel``. Saving is done by the list controller, which
    reads ``get_data()`` after the dialog is accepted.
    """

    def __init__(
        self,
        view: "ProfessionalEditView",
        professional: Optional["Professional"] = None,
        message_service: Optional[MessageService] = None,
    ) -> None:
        self.view = view
        self.service = ProfessionalService()
        self.professional = professional
        self.ok_clicked = False
        self.msg = message_service or MessageService(view)
        self._initialize_view()

        self.view.pb_ok.clicked.connect(self.handle_ok)
        self.view.pb_cancel.clicked.connect(self.handle_cancel)

    def _initialize_view(self):
        """Fill the form, with the edited professional if any.

        The type and institution combo boxes are filled first; for a new
        professional, their first item is selected.
        """
        self.list_types()
        self.list_institutions()

        if self.professional:
            self.view.led_name.setText(self.professional.name)

            index = self.view.cbx_type.findData(self.professional.type)
            self.view.cbx_type.setCurrentIndex(index)

            index = self.view.cbx_institution.findData(
                self.professional.institutionfacility.id
            )
            self.view.cbx_institution.setCurrentIndex(index)
        else:
            self.view.cbx_type.setCurrentIndex(0)
            self.view.cbx_institution.setCurrentIndex(0)

    def list_types(self) -> None:
        """Fill the type combo box with the translated types."""
        self.view.cbx_type.clear()

        types = self.service.get_professional_types()
        for type_id, type_name in types.items():
            self.view.cbx_type.addItem(type_name, type_id)

    def list_institutions(self) -> None:
        """Fill the institution combo box, sorted by name."""
        self.view.cbx_institution.clear()

        institutions = self.service.get_all_institutionfacilities()
        for institution in institutions:
            self.view.cbx_institution.addItem(institution.name, institution.id)

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
            Keys ``"id"`` (the edited professional's ID, or 0 for a new
            one), ``"name"``, ``"type"`` (type code) and
            ``"institutionfacility"`` (the selected
            ``InstitutionFacility``, or None).
        """
        institution_id = self.view.cbx_institution.currentData()
        institution = self.service.get_institutionfacility_by_id(
            institution_id
        )

        return {
            "id": (
                self.professional.id
                if self.professional and self.professional.id != 0
                else 0
            ),
            "name": self.view.led_name.text(),
            "type": self.view.cbx_type.currentData(),
            "institutionfacility": institution,
        }
