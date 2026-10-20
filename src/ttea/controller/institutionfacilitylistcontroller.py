"""Controller of the institution facility list window."""

from typing import TYPE_CHECKING, Callable, Dict

from PySide6.QtCore import QObject

from ttea.exception import BusinessRuleException
from ttea.service import InstitutionFacilityService
from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.view import (
        InstitutionFacilityEditView,
        InstitutionFacilityListView,
    )


class InstitutionFacilityListController(QObject):
    """Controller of the institution facility list window (MVCS).

    Mediates between ``InstitutionFacilityListView`` and
    ``InstitutionFacilityService``: loads and filters the table, shows
    the details of the selected institution facility and opens the edit
    dialog to create or update institution facilities.

    Parameters
    ----------
    view : InstitutionFacilityListView
        The list view.
    factory : Callable
        Creates the edit dialog: ``factory(parent,
        institutionfacility=None)`` returns
        ``InstitutionFacilityEditView``.

    Attributes
    ----------
    view : InstitutionFacilityListView
        The list view.
    factory : Callable
        Factory of the edit dialog.
    service : InstitutionFacilityService
        Shared service of institution facilities.
    msg : MessageService
        Service used to show messages.

    Notes
    -----
    The table is reloaded automatically when the service emits
    ``institutionfacility_change`` (observer pattern), keeping the
    current search text. The buttons, search field and table selection
    are connected when the controller is created, and the table is
    loaded right away. Messages are translated with ``self.tr()``.
    """

    def __init__(
        self, view: "InstitutionFacilityListView", factory: Callable
    ) -> None:
        self.view = view
        self.factory = factory
        self.service = InstitutionFacilityService()
        self.msg = MessageService(self.view)

        self.service.institutionfacility_change.connect(self.reload_data)

        self.view.pb_new.clicked.connect(self.create_institutionfacility)
        self.view.pb_edit.clicked.connect(self.update_institutionfacility)
        self.view.pb_delete.clicked.connect(self.delete_institutionfacility)
        self.view.led_search.textChanged.connect(
            self.filter_institutionfacilities
        )
        self.view.tbl_institution.itemSelectionChanged.connect(
            self.on_table_selection
        )

        self.load_institutionfacilities()

    def reload_data(self, target_id: int = 0) -> None:
        """Reload the table after a change in the service.

        Slot of
        ``InstitutionFacilityService.institutionfacility_change``.

        Parameters
        ----------
        target_id : int, optional
            ID to select after reloading. With 0 (default), the
            currently selected row is kept.
        """
        if target_id == 0:
            target_id = self.view.get_selected_id() or 0

        query = self.view.led_search.text()
        self.load_institutionfacilities(query)

        if target_id > 0:
            self.view.select_row_by_id(target_id)

    def load_institutionfacilities(self, query: str = "") -> None:
        """Load the institution facilities matching ``query``.

        Parameters
        ----------
        query : str, optional
            Search term; empty lists all institution facilities. Default
            is ``""``.

        Notes
        -----
        The details panel is cleared.
        """
        institutionfacilities = self.service.search_institutionfacilities(
            query
        )
        self.view.populate_table(institutionfacilities)
        self.view.clear_details()

    def filter_institutionfacilities(self, text: str) -> None:
        """Filter the table with the search text.

        Parameters
        ----------
        text : str
            Text typed in the search field; it is stripped.
        """
        self.load_institutionfacilities(text.strip())

    def on_table_selection(self) -> None:
        """Show the details of the selected institution facility."""
        institutionfacility_id = self.view.get_selected_id()
        if institutionfacility_id:
            institutionfacility = self.service.find_by_id(
                institutionfacility_id
            )

            if institutionfacility:
                self.view.display_details(institutionfacility)
        else:
            self.view.clear_details()

    def create_institutionfacility(self) -> None:
        """Create an institution facility through the edit dialog."""
        dialog: "InstitutionFacilityEditView" = self.factory(self.view, None)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.create_institutionfacility(data):
                self.msg.info(
                    self.tr(
                        "Instituição/Estabelecimento cadastrada com sucesso!"
                    )
                )
            else:
                self.msg.critical(
                    self.tr("Erro ao salvar instituição/estabelecimento.")
                )

    def update_institutionfacility(self) -> None:
        """Edit the selected institution facility in the edit dialog.

        Notes
        -----
        A warning is shown when no row is selected.
        """
        institutionfacility_id = self.view.get_selected_id()
        if not institutionfacility_id:
            self.msg.warning(
                self.tr(
                    "Selecione uma instituição/estabelecimento para editar."
                )
            )
            return

        institutionfacility = self.service.find_by_id(institutionfacility_id)
        if not institutionfacility:
            self.msg.critical(
                self.tr("Instituição/Estabelecimento não encontrada.")
            )
            return

        dialog: "InstitutionFacilityEditView" = self.factory(
            self.view, institutionfacility
        )
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.update_institutionfacility(
                institutionfacility_id, data
            ):
                self.msg.info(
                    self.tr(
                        "Instituição/Estabelecimento atualizada com sucesso."
                    )
                )
            else:
                self.msg.critical(
                    self.tr("Erro ao atualizar instituição/estabelecimento.")
                )

    def delete_institutionfacility(self) -> None:
        """Delete the selected institution facility after confirmation.

        Notes
        -----
        A warning is shown when no row is selected.
        ``BusinessRuleException`` from the service (e.g. a linked
        record) is shown as a warning.
        """
        institutionfacility_id = self.view.get_selected_id()
        if not institutionfacility_id:
            self.msg.warning(
                self.tr(
                    "Selecione uma instituição/estabelecimento para excluir."
                )
            )
            return

        institutionfacility = self.service.find_by_id(institutionfacility_id)
        if not institutionfacility:
            return

        if self.msg.question(
            self.tr("Deseja excluir?\n{0}").format(institutionfacility.name)
        ):
            try:
                if self.service.delete_institutionfacility(
                    institutionfacility_id
                ):
                    self.view.clear_details()
                    self.msg.info(
                        self.tr(
                            "Instituição/Estabelecimento excluída com sucesso."
                        )
                    )
                else:
                    self.msg.critical(
                        self.tr("Erro ao excluir instituição/estabelecimento.")
                    )
            except BusinessRuleException as e:
                self.msg.warning(str(e))

    def get_institutionfacility_types(self) -> Dict[int, str]:
        """Return the institution facility types with translated names.

        Returns
        -------
        dict[int, str]
            Type code to translated name, from the service.
        """
        return self.service.get_institutionfacility_types()
