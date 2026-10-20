"""Controller of the professional list window."""

from typing import TYPE_CHECKING, Callable, Dict

from PySide6.QtCore import QObject

from ttea.service import ProfessionalService
from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.view import ProfessionalEditView, ProfessionalListView


class ProfessionalListController(QObject):
    """Controller of the professional list window (MVCS).

    Mediates between ``ProfessionalListView`` and
    ``ProfessionalService``: loads and filters the table, shows the
    details of the selected professional and opens the edit dialog to
    create or update professionals.

    Parameters
    ----------
    view : ProfessionalListView
        The list view.
    factory : Callable
        Creates the edit dialog: ``factory(parent, professional=None)``
        returns ``ProfessionalEditView``.

    Attributes
    ----------
    view : ProfessionalListView
        The list view.
    factory : Callable
        Factory of the edit dialog.
    service : ProfessionalService
        Shared service of professionals.
    msg : MessageService
        Service used to show messages.

    Notes
    -----
    The table is reloaded automatically when the service emits
    ``professional_change`` (observer pattern), keeping the current
    search text. The buttons, search field and table selection are
    connected when the controller is created, and the table is loaded
    right away. Messages are translated with ``self.tr()``.
    """

    def __init__(
        self, view: "ProfessionalListView", factory: Callable
    ) -> None:
        self.view = view
        self.factory = factory
        self.service = ProfessionalService()
        self.msg = MessageService(self.view)

        self.service.professional_change.connect(self.reload_data)

        self.view.pb_new.clicked.connect(self.create_professional)
        self.view.pb_edit.clicked.connect(self.update_professional)
        self.view.pb_delete.clicked.connect(self.delete_professional)
        self.view.led_search.textChanged.connect(self.filter_professionals)
        self.view.tbl_professional.selectionModel().selectionChanged.connect(
            self.on_table_selection
        )

        self.load_professionals()

    def reload_data(self, target_id: int = 0) -> None:
        """Reload the table after a change in the service.

        Slot of ``ProfessionalService.professional_change``.

        Parameters
        ----------
        target_id : int, optional
            ID to select after reloading. With 0 (default), the
            currently selected row is kept.
        """
        if target_id == 0:
            target_id = self.view.get_selected_id() or 0

        query = self.view.led_search.text()
        self.load_professionals(query)

        if target_id > 0:
            self.view.select_row_by_id(target_id)

    def load_professionals(self, query: str = "") -> None:
        """Load the professionals matching ``query``.

        Parameters
        ----------
        query : str, optional
            Search term; empty lists all professionals. Default is
            ``""``.

        Notes
        -----
        The details panel is cleared.
        """
        load_professionals = self.service.search_professionals(query)
        self.view.populate_table(load_professionals)
        self.view.clear_details()

    def filter_professionals(self, text: str) -> None:
        """Filter the table with the search text.

        Parameters
        ----------
        text : str
            Text typed in the search field; it is stripped.
        """
        self.load_professionals(text.strip())

    def on_table_selection(self) -> None:
        """Show the details of the selected professional."""
        professional_id = self.view.get_selected_id()
        if professional_id:
            professional = self.service.find_by_id(professional_id)

            if professional:
                self.view.display_details(professional)
        else:
            self.view.clear_details()

    def create_professional(self) -> None:
        """Create a professional through the edit dialog."""
        dialog: "ProfessionalEditView" = self.factory(self.view, None)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.create_professional(data):
                self.msg.info(self.tr("Profissional cadastrado com sucesso!"))
            else:
                self.msg.critical(self.tr("Erro ao salvar profissional."))

    def update_professional(self) -> None:
        """Edit the selected professional through the edit dialog.

        Notes
        -----
        A warning is shown when no row is selected.
        """
        professional_id = self.view.get_selected_id()
        if not professional_id:
            self.msg.warning(self.tr("Selecione um profissional para editar."))
            return

        professional = self.service.find_by_id(professional_id)
        if not professional:
            self.msg.critical(self.tr("Profissional não encontrado."))
            return

        dialog: "ProfessionalEditView" = self.factory(self.view, professional)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.update_professional(professional_id, data):
                self.msg.info(self.tr("Profissional atualizado com sucesso."))
            else:
                self.msg.critical(self.tr("Erro ao atualizar profissional."))

    def delete_professional(self) -> None:
        """Delete the selected professional after confirmation.

        Notes
        -----
        A warning is shown when no row is selected.
        """
        professional_id = self.view.get_selected_id()
        if not professional_id:
            self.msg.warning(
                self.tr("Selecione um profissional para excluir.")
            )
            return

        professional = self.service.find_by_id(professional_id)
        if not professional:
            return

        if self.msg.question(
            self.tr("Deseja excluir?\n{0}").format(professional.name)
        ):
            if self.service.delete_professional(professional_id):
                self.view.clear_details()
                self.msg.info(self.tr("Profissional excluído com sucesso."))
            else:
                self.msg.critical(self.tr("Erro ao excluir profissional."))

    def get_professional_types(self) -> Dict[int, str]:
        """Return the professional types with translated names.

        Returns
        -------
        dict[int, str]
            Type code to translated name, from the service.
        """
        return self.service.get_professional_types()
