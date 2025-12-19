from typing import TYPE_CHECKING, Callable, Optional

# Local module import
from udescjoinvilletteaservice import PlayerService
from udescjoinvilletteautil import MessageService

if TYPE_CHECKING:
    from udescjoinvilletteamodel import Player
    from udescjoinvilletteaview import PlayerEditView, PlayerListView


class PlayerListController:
    """
    Lightweight controller that orchestrates PlayerListView and PlayerService.

    Follows MVCS pattern: mediates between view and service layer,
    handling user interactions and updating the UI accordingly.

    Attributes
    ----------
    view : PlayerListView
        Main view displaying the list and details of players.
    factory : Callable
        Factory function that creates a ``PlayerEditView`` dialog,
        receiving the parent view and an optional player to edit.
    service : PlayerService
        Business logic layer for player CRUD operations.
    msg : MessageService
        Helper for showing info, warning, and error messages.

    Methods
    -------
    __init__(view, player_edit_view_factory)
        Initializes the controller with view and edit dialog factory.
    load_players(query="")
        Loads and displays players, optionally filtered by search term.
    filter_players(text)
        Filters the player list based on the search input text.
    on_table_selection()
        Updates details panel when a table row is selected.
    select_and_show_player(player_id)
        Selects a player row and shows its details.
    handle_new_player()
        Opens dialog to create a new player.
    handle_edit_player()
        Opens dialog to edit the selected player.
    delete_player()
        Deletes the selected player after confirmation.
    """

    def __init__(
        self,
        view: "PlayerListView",
        player_edit_view_factory: Callable[
            [Optional["PlayerListView"], Optional["Player"]], "PlayerEditView"
        ],
    ) -> None:
        """
        Initialize the controller.

        Parameters
        ----------
        view : PlayerListView
            The main list view instance to control.
        player_edit_view_factory : Callable
            Function that returns a ``PlayerEditView`` dialog.
            Signature: (parent_view, player) -> PlayerEditView.
        """
        self.view = view
        self.factory = player_edit_view_factory
        self.service = PlayerService()  # ← Serviço injetado
        self.msg = MessageService(view)

    def load_players(self, query: str = "") -> None:
        """
        Load players from service and populate the table view.

        Parameters
        ----------
        query : str, optional
            Search term to filter players (default is empty string).
        """
        players = self.service.search_players(query)
        self.view.populate_table(players)
        self.view.clear_details()

    def filter_players(self, text: str) -> None:
        """Filter player list based on search input text."""
        self.load_players(text.strip())

    def on_table_selection(self) -> None:
        """Update details pane when a player is selected in the table."""
        player_id = self.view.get_selected_player_id()
        if player_id is not None:
            player = self.service.find_by_id(player_id)
            self.view.display_player_details(player)
        else:
            self.view.clear_details()

    def select_and_show_player(self, player_id: int) -> None:
        """
        Select a player row by ID and display its details.

        Parameters
        ----------
        player_id : int
            The ID of the player to select and show.
        """
        player = self.service.find_by_id(player_id)
        if player:
            self.view.display_player_details(player)
            self.view.select_row_by_id(player_id)

    def handle_new_player(self) -> None:
        """Open dialog to create a new player and save if accepted."""
        dialog = self.factory(self.view, None)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        player = self.service.create_player(data)
        if player:
            self.load_players(self.view.search_input.text())
            self.select_and_show_player(player.id)
            self.msg.info(self.view.tr("Jogador cadastrado com sucesso!"))
        else:
            self.msg.critical(self.view.tr("Erro ao salvar jogador."))

    def handle_edit_player(self) -> None:
        """Open dialog to edit the selected player and update if accepted."""
        player_id = self.view.get_selected_player_id()
        if not player_id:
            self.msg.warning(self.view.tr("Selecione um jogador para editar."))
            return

        player = self.service.find_by_id(player_id)
        if not player:
            self.msg.critical(self.view.tr("Jogador não encontrado."))
            return

        dialog = self.factory(self.view, player)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        if self.service.update_player(player_id, data):
            self.load_players(self.view.search_input.text())
            self.select_and_show_player(player_id)
            self.msg.info(self.view.tr("Jogador atualizado com sucesso."))
        else:
            self.msg.critical(self.view.tr("Erro ao atualizar jogador."))

    def delete_player(self) -> None:
        """Delete the selected player after user confirmation."""
        player_id = self.view.get_selected_player_id()
        if not player_id:
            self.msg.warning(
                self.view.tr("Selecione um jogador para excluir.")
            )
            return

        player = self.service.find_by_id(player_id)
        if not player:
            return

        if self.msg.question(
            self.view.tr(f"Tem certeza que deseja excluir?\n{player.name}")
        ):
            if self.service.delete_player(player_id):
                self.load_players(self.view.search_input.text())
                self.view.clear_details()
                self.msg.info(self.view.tr("Jogador excluído com sucesso."))
            else:
                self.msg.critical(self.view.tr("Erro ao excluir jogador."))
