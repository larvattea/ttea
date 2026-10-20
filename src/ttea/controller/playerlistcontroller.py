"""Controller of the player list window."""

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QObject

from ttea.exception import BusinessRuleException
from ttea.service import PlayerService
from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.view import PlayerEditView, PlayerListView


class PlayerListController(QObject):
    """Controller of the player list window (MVCS).

    Mediates between ``PlayerListView`` and ``PlayerService``: loads and
    filters the table, shows the details of the selected player and
    opens the edit dialog to create or update players.

    Parameters
    ----------
    view : PlayerListView
        The list view.
    factory : Callable
        Creates the edit dialog: ``factory(parent, player=None)``
        returns ``PlayerEditView``.

    Attributes
    ----------
    view : PlayerListView
        The list view.
    factory : Callable
        Factory of the edit dialog.
    service : PlayerService
        Shared service of players.
    msg : MessageService
        Service used to show messages.

    Notes
    -----
    The table is reloaded automatically when the service emits
    ``player_change`` (observer pattern), keeping the current search
    text. The buttons, search field and table selection are connected
    when the controller is created, and the table is loaded right away.
    Messages are translated with ``self.tr()``.
    """

    def __init__(self, view: "PlayerListView", factory: Callable):
        self.view = view
        self.factory = factory
        self.service = PlayerService()
        self.msg = MessageService(self.view)

        self.service.player_change.connect(self.reload_data)

        self.view.pb_new.clicked.connect(self.create_player)
        self.view.pb_edit.clicked.connect(self.update_player)
        self.view.pb_delete.clicked.connect(self.delete_player)
        self.view.led_search.textChanged.connect(self.filter_players)
        self.view.tbl_player.itemSelectionChanged.connect(
            self.on_table_selection
        )

        self.load_players()

    def reload_data(self, target_id: int = 0) -> None:
        """Reload the table after a change in the service.

        Slot of ``PlayerService.player_change``.

        Parameters
        ----------
        target_id : int, optional
            ID to select after reloading. With 0 (default), the
            currently selected row is kept.
        """
        if target_id == 0:
            target_id = self.view.get_selected_id() or 0

        query = self.view.led_search.text()
        self.load_players(query)

        if target_id > 0:
            self.view.select_row_by_id(target_id)

    def load_players(self, query: str = "") -> None:
        """Load the players matching ``query``.

        Parameters
        ----------
        query : str, optional
            Search term; empty lists all players. Default is ``""``.

        Notes
        -----
        The details panel is cleared.
        """
        players = self.service.search_players(query)
        self.view.populate_table(players)
        self.view.clear_details()

    def filter_players(self, text: str) -> None:
        """Filter the table with the search text.

        Parameters
        ----------
        text : str
            Text typed in the search field; it is stripped.
        """
        self.load_players(text.strip())

    def on_table_selection(self) -> None:
        """Show the details of the selected player."""
        player_id = self.view.get_selected_id()
        if player_id:
            player = self.service.find_by_id(player_id)
            if player:
                self.view.display_details(player)
        else:
            self.view.clear_details()

    def create_player(self) -> None:
        """Create a player through the edit dialog."""
        dialog: "PlayerEditView" = self.factory(self.view)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.create_player(data):
                # The service signal reloads the list.
                self.msg.info(self.tr("Jogador cadastrado com sucesso!"))
            else:
                self.msg.critical(self.tr("Erro ao salvar jogador."))

    def update_player(self) -> None:
        """Edit the selected player through the edit dialog.

        Notes
        -----
        A warning is shown when no row is selected.
        """
        player_id = self.view.get_selected_id()
        if not player_id:
            self.msg.warning(self.tr("Selecione um jogador para editar."))
            return

        player = self.service.find_by_id(player_id)
        if not player:
            self.msg.critical(self.tr("Jogador não encontrado."))
            return

        dialog: "PlayerEditView" = self.factory(self.view, player)
        if dialog.exec():
            data = dialog.controller.get_data()
            if self.service.update_player(player_id, data):
                # The service signal reloads the list.
                self.msg.info(self.tr("Jogador atualizado com sucesso."))
            else:
                self.msg.critical(self.tr("Erro ao atualizar jogador."))

    def delete_player(self) -> None:
        """Delete the selected player after confirmation.

        Notes
        -----
        A warning is shown when no row is selected.
        ``BusinessRuleException`` from the service (e.g. a linked
        record) is shown as a warning.
        """
        player_id = self.view.get_selected_id()
        if not player_id:
            self.msg.warning(self.tr("Selecione um jogador para excluir."))
            return

        player = self.service.find_by_id(player_id)
        if not player:
            return

        if self.msg.question(
            self.tr("Deseja excluir?\n{0}").format(player.name)
        ):
            try:
                if self.service.delete_player(player_id):
                    self.view.clear_details()
                    self.msg.info(self.tr("Jogador excluído com sucesso."))
                else:
                    self.msg.critical(self.tr("Erro ao excluir jogador."))
            except BusinessRuleException as e:
                self.msg.warning(str(e))
