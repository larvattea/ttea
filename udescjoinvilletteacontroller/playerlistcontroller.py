from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from udescjoinvilletteadao import PlayerCsvDAO
from udescjoinvilletteamodel import Player

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteaview import PlayerEditView, PlayerListView


class PlayerListController:
    """Controller to handle UI interactions and business logic for player list.

    Parameters
    ----------
    view : PlayerListView
        The view instance for displaying player data.
    player_edit_view_factory : Callable[[Optional[QDialog], Optional[Player]],
                                        PlayerEditView]
        Factory function to create PlayerEditView instances.

    Attributes
    ----------
    view : PlayerListView
        The view instance for displaying player data.
    dao : PlayerCsvDAO
        Data access object for player data operations.
    player_edit_view_factory : Callable[[Optional[QDialog], Optional[Player]],
                                        PlayerEditView]
        Factory function to create PlayerEditView instances.

    Methods
    -------
    load_players(search_query: str = "") -> None
        Load players into the table, optionally filtered by search query.
    filter_players() -> None
        Filter players based on search input and refresh table.
    handle_new_player() -> None
        Open dialog to create a new player.
    handle_edit_player() -> None
        Open dialog to edit selected player.
    delete_player() -> None
        Delete selected player.
    show_player_details(player: Optional[Player]) -> None
        Show details of the selected player in the labels.
    on_table_selection() -> None
        Populate details labels when a table row is selected.
    """

    def __init__(
        self,
        view: "PlayerListView",
        player_edit_view_factory: Callable[
            [Optional[QDialog], Optional[Player]], "PlayerEditView"
        ],
    ) -> None:
        """Initialize the controller with a view and a factory for
        PlayerEditView.

        Parameters
        ----------
        view : PlayerListView
            The view instance for displaying player data.
        player_edit_view_factory : Callable[[Optional[QDialog],
                                            Optional[Player]], PlayerEditView]
            Factory function to create PlayerEditView instances.

        Returns
        -------
        None
        """
        self.view = view
        self.dao = PlayerCsvDAO()
        self.player_edit_view_factory = player_edit_view_factory

    def load_players(self, search_query: str = "") -> None:
        """Load players into the table, optionally filtered by search query.

        Parameters
        ----------
        search_query : str, optional
            Query to filter players by name or ID (default is "").

        Returns
        -------
        None

        Notes
        -----
        - Filters players if search_query is provided, matching against ID
            or name.
        - Updates the table with filtered or all players.
        - Clears player details display when reloading.
        """
        players = self.dao.list()

        # Filter players by name or ID if search query is provided
        if search_query:
            search_query = search_query.lower()
            players = [
                player
                for player in players
                if (
                    search_query in str(player.id)
                    or search_query in player.name.lower()
                )
            ]
        self.view.table.setRowCount(len(players))
        for row, player in enumerate(players):
            self.view.table.setItem(row, 0, QTableWidgetItem(str(player.id)))
            self.view.table.setItem(row, 1, QTableWidgetItem(player.name))
            self.view.table.setItem(
                row,
                2,
                QTableWidgetItem(player.birth_date.strftime("%Y-%m-%d")),
            )
            self.view.table.setItem(
                row, 3, QTableWidgetItem(player.observation)
            )

        # Clear details when reloading players
        self.show_player_details(None)

    def filter_players(self) -> None:
        """Filter players based on search input and refresh table.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves the search query from the view's search input.
        - Calls load_players with the search query to update the table.
        """
        search_query = self.view.search_input.text()
        self.load_players(search_query)

    def handle_new_player(self) -> None:
        """Open dialog to create a new player.

        Returns
        -------
        None

        Notes
        -----
        - Creates a new player dialog using the factory.
        - Inserts new player into the database if dialog is accepted.
        - Displays success or failure message based on insertion result.
        - Reloads the player list after successful insertion.
        """
        dialog = self.player_edit_view_factory(self.view)
        if dialog.exec():
            data = dialog.controller.get_player_data()
            player_id = len(self.dao.list()) + 1
            player = Player(
                id=player_id,
                name=data["name"],
                birth_date=data["birth_date"],
                observation=data["observation"],
            )
            result = self.dao.insert(player)
            if result:
                self.load_players(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Jogador adicionado com sucesso.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Falha ao adicionar um jogador.",
                )

    def handle_edit_player(self) -> None:
        """Open dialog to edit selected player.

        Returns
        -------
        None

        Notes
        -----
        - Checks if a player is selected; shows warning if not.
        - Retrieves selected player's data and opens edit dialog.
        - Updates player data if dialog is accepted and saves changes.
        - Displays success or failure message based on update result.
        - Reloads the player list after successful update.
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                "Por favor selecione um jogador para editar.",
            )
            return
        player_id = int(self.view.table.item(selected[0].row(), 0).text())
        player = self.dao.select(player_id)
        if not player:
            QMessageBox.critical(self.view, "Erro", "Jogador não encontrado.")
            return
        dialog = self.player_edit_view_factory(self.view, player)
        if dialog.exec() and dialog.controller.ok_clicked:
            data = dialog.controller.get_player_data()
            updated_player = Player(
                id=player_id,
                name=data["name"],
                birth_date=data["birth_date"],
                observation=data["observation"],
            )
            result = self.dao.update(updated_player)
            if result:
                self.load_players(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Dados do jogador atualizados.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Falha ao atualizar os dados do jogador.",
                )

    def delete_player(self) -> None:
        """Delete selected player.

        Returns
        -------
        None

        Notes
        -----
        - Checks if a player is selected; shows warning if not.
        - Prompts user to confirm deletion with player name.
        - Deletes player if confirmed and displays success or failure message.
        - Reloads the player list after successful deletion.
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                "Por favor selecione um jogador para excluir.",
            )
            return
        player_id = int(self.view.table.item(selected[0].row(), 0).text())
        player_name = self.view.table.item(selected[0].row(), 1).text()
        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.view.parent().windowIcon())
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.view.parent().windowTitle())
        msg_box.setText(
            self.view.parent().tr(
                f"Confirma a exclusão do jogador?\n{player_name}"
            )
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText(self.view.parent().tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.view.parent().tr("Não"))
        if msg_box.exec() == QMessageBox.Yes:
            result = self.dao.delete(player_id)
            if result:
                self.load_players(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Jogador excluído com sucesso.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Não foi possível excluir o jogador.",
                )

    def show_player_details(self, player: Optional[Player]) -> None:
        """Show details of the selected player in the labels.

        Parameters
        ----------
        player : Optional[Player]
            The player object to display details for, or None to clear.

        Returns
        -------
        None

        Notes
        -----
        - Displays player ID, name, birth date, and observation in view labels.
        - Clears labels if no player is provided.
        """
        if player:
            self.view.id_label.setText(str(player.id))
            self.view.name_label.setText(player.name)
            self.view.birth_date_label.setText(
                player.birth_date.strftime("%Y-%m-%d")
            )
            self.view.observation_label.setText(player.observation)
        else:
            self.view.id_label.setText("")
            self.view.name_label.setText("")
            self.view.birth_date_label.setText("")
            self.view.observation_label.setText("")

    def on_table_selection(self) -> None:
        """Populate details labels when a table row is selected.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves selected player's ID from the table.
        - Fetches player data and updates details labels via
            show_player_details.
        - Clears details if no row is selected.
        """
        selected = self.view.table.selectedItems()
        if selected:
            player_id = int(self.view.table.item(selected[0].row(), 0).text())
            player = self.dao.select(player_id)
            self.show_player_details(player)
        else:
            self.show_player_details(None)
