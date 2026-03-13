from typing import TYPE_CHECKING, Callable, Dict

from PySide6.QtCore import QObject

# Local module import
from udescjoinvilletteaservice import HealthProfessionalService
from udescjoinvilletteautil import MessageService

if TYPE_CHECKING:
    from udescjoinvilletteaview import (HealthProfessionalEditView,
                                        HealthProfessionalListView)


class HealthProfessionalListController(QObject):
    """
    Lightweight controller that orchestrates InstitutionFacilityListView
    and InstitutionFacilityService.

    Follows MVCS pattern: mediates between view and service layer,
    handling user interactions and updating the UI accordingly.

    Attributes
    ----------
    view : InstitutionFacilityListView
        Main view displaying the list and details of healthprofessionals.
    factory : Callable
        Factory function that creates a ``InstitutionFacilityEditView`` dialog,
        receiving the parent view and an optional healthprofessional to edit.
    service : InstitutionFacilityService
        Business logic layer for healthprofessional CRUD operations.
    msg : MessageService
        Helper for showing info, warning, and error messages.

    Methods
    -------
    __init__(view, healthprofessional_edit_view_factory)
        Initializes the controller with view and edit dialog factory.
    load_healthprofessionals(query="")
        Loads and displays healthprofessionals, optionally filtered
        by search term.
    filter_healthprofessionals(text)
        Filters the healthprofessional list based on the search input text.
    on_table_selection()
        Updates details panel when a table row is selected.
    select_and_show_healthprofessional(healthprofessional_id)
        Selects a healthprofessional row and shows its details.
    handle_new_healthprofessional()
        Opens dialog to create a new healthprofessional.
    handle_edit_healthprofessional()
        Opens dialog to edit the selected healthprofessional.
    delete_healthprofessional()
        Deletes the selected healthprofessional after confirmation.
    """

    def __init__(
        self, view: "HealthProfessionalListView", factory: Callable
    ) -> None:
        """
        Initialize the controller.

        Parameters
        ----------
        view : HealthProfessionalListView
            The main list view instance to control.
        healthprofessional_edit_view_factory : Callable
            Function that returns a ``HealthProfessionalEditView`` dialog.
            Signature: (parent_view, healthprofessional)
            -> HealthProfessionalEditView.
        """
        self.view = view
        self.factory = factory
        self.service = HealthProfessionalService()
        self.msg = MessageService(self.view)

        # ------------------------------------------------------------------
        # OBSERVER PATTERN: Conexão reativa
        # ------------------------------------------------------------------
        # Sempre que o serviço emitir que os dados mudaram, a lista recarrega.
        self.service.healthprofessional_change.connect(self.reload_data)

        # Events signals and slots
        self.view.pb_new.clicked.connect(self.create_healthprofessional)
        self.view.pb_edit.clicked.connect(self.update_healthprofessional)
        self.view.pb_delete.clicked.connect(self.delete_healthprofessional)
        self.view.led_search.textChanged.connect(
            self.filter_healthprofessionals
        )
        self.view.tbl_health.selectionModel().selectionChanged.connect(
            self.on_table_selection
        )

        # Carga inicial
        self.load_healthprofessionals()

    def reload_data(self, target_id: int = 0) -> None:
        """
        Slot que reage ao sinal do Service.
        Mantém o filtro atual ao recarregar.
        """
        if target_id == 0:
            target_id = self.view.get_selected_id() or 0

        query = self.view.led_search.text()
        self.load_healthprofessionals(query)

        if target_id > 0:
            self.view.select_row_by_id(target_id)

    def load_healthprofessionals(self, query: str = "") -> None:
        """
        Load load_healthprofessionals from service
        and populate the table view.

        Parameters
        ----------
        query : str, optional
            Search term to filter healthprofessionals
            (default is empty string).
        """
        load_healthprofessionals = self.service.search_healthprofessionals(
            query
        )
        self.view.populate_table(load_healthprofessionals)
        self.view.clear_details()

    def filter_healthprofessionals(self, text: str) -> None:
        """Filter healthprofessional list based on search input text."""
        self.load_healthprofessionals(text.strip())

    def on_table_selection(self) -> None:
        """Update details pane when a healthprofessional
        is selected in the table."""
        healthprofessional_id = self.view.get_selected_id()
        if healthprofessional_id:
            healthprofessional = self.service.find_by_id(healthprofessional_id)

            if healthprofessional:
                self.view.display_details(healthprofessional)
        else:
            self.view.clear_details()

    def create_healthprofessional(self) -> None:
        """Open dialog to create a new healthprofessional
        and save if accepted."""
        dialog: "HealthProfessionalEditView" = self.factory(self.view, None)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.create_healthprofessional(data):
                self.msg.info(
                    self.tr("Profissional de saúde cadastrado com sucesso!")
                )
            else:
                self.msg.critical(
                    self.tr("Erro ao salvar profissional de saúde.")
                )

    def update_healthprofessional(self) -> None:
        """Open dialog to edit the selected healthprofessional
        and update if accepted."""
        healthprofessional_id = self.view.get_selected_id()
        if not healthprofessional_id:
            self.msg.warning(
                self.tr("Selecione um professional de saúde para editar.")
            )
            return

        healthprofessional = self.service.find_by_id(healthprofessional_id)
        if not healthprofessional:
            self.msg.critical(self.tr("Professional de saúde não encontrada."))
            return

        dialog: "HealthProfessionalEditView" = self.factory(
            self.view, healthprofessional
        )
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.update_healthprofessional(
                healthprofessional_id, data
            ):
                self.msg.info(
                    self.tr("Professional de saúde atualizado com sucesso.")
                )
            else:
                self.msg.critical(
                    self.tr("Erro ao atualizar professional de saúde.")
                )

    def delete_healthprofessional(self) -> None:
        """Delete the selected healthprofessional after user confirmation."""

        healthprofessional_id = self.view.get_selected_id()
        if not healthprofessional_id:
            self.msg.warning(
                self.tr("Selecione um professional de saúde para excluir.")
            )
            return

        healthprofessional = self.service.find_by_id(healthprofessional_id)
        if not healthprofessional:
            return

        if self.msg.question(
            self.tr("Deseja excluir?\n{0}").format(healthprofessional.name)
        ):
            if self.service.delete_healthprofessional(healthprofessional_id):
                self.view.clear_details()
                self.msg.info(
                    self.tr("Professional de saúde excluído com sucesso.")
                )
            else:
                self.msg.critical(
                    self.tr("Erro ao excluir professional de saúde.")
                )

    def get_healthprofessional_types(self) -> Dict[int, str]:
        return self.service.get_healthprofessional_types()
