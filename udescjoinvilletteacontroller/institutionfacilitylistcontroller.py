from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject

# Local module import
from udescjoinvilletteaservice import InstitutionFacilityService
from udescjoinvilletteautil import MessageService

if TYPE_CHECKING:
    from udescjoinvilletteamodel import InstitutionFacility
    from udescjoinvilletteaview import (InstitutionFacilityEditView,
                                        InstitutionFacilityListView)


class InstitutionFacilityListController(QObject):
    """
    Lightweight controller that orchestrates InstitutionFacilityListView
    and InstitutionFacilityService.

    Follows MVCS pattern: mediates between view and service layer,
    handling user interactions and updating the UI accordingly.

    Attributes
    ----------
    view : InstitutionFacilityListView
        Main view displaying the list and details of institutionfacilities.
    factory : Callable
        Factory function that creates a ``InstitutionFacilityEditView`` dialog,
        receiving the parent view and an optional institutionfacility to edit.
    service : InstitutionFacilityService
        Business logic layer for institutionfacility CRUD operations.
    msg : MessageService
        Helper for showing info, warning, and error messages.

    Methods
    -------
    __init__(view, institutionfacility_edit_view_factory)
        Initializes the controller with view and edit dialog factory.
    load_institutionfacilities(query="")
        Loads and displays institutionfacilities, optionally filtered
        by search term.
    filter_institutionfacilities(text)
        Filters the institutionfacility list based on the search input text.
    on_table_selection()
        Updates details panel when a table row is selected.
    select_and_show_institutionfacility(institutionfacility_id)
        Selects a institutionfacility row and shows its details.
    handle_new_institutionfacility()
        Opens dialog to create a new institutionfacility.
    handle_edit_institutionfacility()
        Opens dialog to edit the selected institutionfacility.
    delete_institutionfacility()
        Deletes the selected institutionfacility after confirmation.
    """

    def __init__(
        self,
        view: "InstitutionFacilityListView",
        institutionfacility_edit_view_factory: Callable[
            [
                Optional["InstitutionFacilityListView"],
                Optional["InstitutionFacility"],
            ],
            "InstitutionFacilityEditView",
        ],
    ) -> None:
        """
        Initialize the controller.

        Parameters
        ----------
        view : InstitutionFacilityListView
            The main list view instance to control.
        institutionfacility_edit_view_factory : Callable
            Function that returns a ``InstitutionFacilityEditView`` dialog.
            Signature: (parent_view, institutionfacility)
            -> InstitutionFacilityEditView.
        """
        self.view = view
        self.factory = institutionfacility_edit_view_factory
        self.service = InstitutionFacilityService()
        self.msg = MessageService(view)

    def load_institutionfacilities(self, query: str = "") -> None:
        """
        Load load_institutionfacilities from service
        and populate the table view.

        Parameters
        ----------
        query : str, optional
            Search term to filter institutionfacilities
            (default is empty string).
        """
        load_institutionfacilities = self.service.search_institutionfacilities(
            query
        )
        self.view.populate_table(load_institutionfacilities)
        self.view.clear_details()

    def filter_institutionfacilities(self, text: str) -> None:
        """Filter institutionfacility list based on search input text."""
        self.load_institutionfacilities(text.strip())

    def on_table_selection(self) -> None:
        """Update details pane when a institutionfacility
        is selected in the table."""
        institutionfacility_id = (
            self.view.get_selected_institutionfacility_id()
        )
        if institutionfacility_id is not None:
            institutionfacility = self.service.find_by_id(
                institutionfacility_id
            )
            self.view.display_institutionfacility_details(institutionfacility)
        else:
            self.view.clear_details()

    def select_and_show_institutionfacility(
        self, institutionfacility_id: int
    ) -> None:
        """
        Select a institutionfacility row by ID and display its details.

        Parameters
        ----------
        institutionfacility_id : int
            The ID of the institutionfacility to select and show.
        """
        institutionfacility = self.service.find_by_id(institutionfacility_id)
        if institutionfacility:
            self.view.display_institutionfacility_details(institutionfacility)
            self.view.select_row_by_id(institutionfacility_id)

    def handle_new_institutionfacility(self) -> None:
        """Open dialog to create a new institutionfacility
        and save if accepted."""
        dialog = self.factory(self.view, None)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        institutionfacility = self.service.create_institutionfacility(data)
        if institutionfacility:
            self.load_institutionfacilities(self.view.led_search.text())
            self.select_and_show_institutionfacility(institutionfacility.id)
            self.msg.info(
                self.tr("Instituição/Estabelecimento cadastrada com sucesso!")
            )
        else:
            self.msg.critical(
                self.tr("Erro ao salvar instuição/estabelecimento.")
            )

    def handle_edit_institutionfacility(self) -> None:
        """Open dialog to edit the selected institutionfacility
        and update if accepted."""
        institutionfacility_id = (
            self.view.get_selected_institutionfacility_id()
        )
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

        dialog = self.factory(self.view, institutionfacility)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        if self.service.update_institutionfacility(
            institutionfacility_id, data
        ):
            self.load_institutionfacilities(self.view.led_search.text())
            self.select_and_show_institutionfacility(institutionfacility_id)
            self.msg.info(
                self.tr("Instituição/Estabelecimento atualizada com sucesso.")
            )
        else:
            self.msg.critical(
                self.tr("Erro ao atualizar instituição/estabelecimento.")
            )

    def delete_institutionfacility(self) -> None:
        """Delete the selected institutionfacility after user confirmation."""
        # from udescjoinvilletteagames.kartea.service import (
        #    PlayerKarteaConfigService,
        # )

        institutionfacility_id = (
            self.view.get_selected_institutionfacility_id()
        )
        if not institutionfacility_id:
            self.msg.warning(
                self.tr(
                    "Selecione uma instituição/estabelecimento para excluir."
                )
            )
            return

        # Add validation with config of games don't delete institutionfacility trocar
        # para ver se não existe profissional de saúde vinculado.
        # karteaconfig = PlayerKarteaConfigService()
        # if karteaconfig.find_config_by_player_id(player_id):
        #    self.msg.warning(
        #        self.tr(
        #            "A exclusão do jogador não é permitida enquanto a configuração do KarTEA existir."
        #        )
        #    )
        #    return

        institutionfacility = self.service.find_by_id(institutionfacility_id)
        if not institutionfacility:
            return

        if self.msg.question(
            self.tr("Tem certeza que deseja excluir?\n{0}").format(
                institutionfacility.name
            )
        ):
            if self.service.delete_institutionfacility(institutionfacility_id):
                self.load_institutionfacilities(self.view.led_search.text())
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
