from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from udescjoinvilletteaapp import AppConfig
# Local module import
from udescjoinvilletteadao import PlayerCsvDAO
from udescjoinvilletteamodel import Player

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteaview import PlayerEditView, PlayerListView


class PlayerListController:
    """Controller to handle UI interactions and business logic for player list.

    This class manages the interaction between the player list view and
    the data access layer, facilitating operations such as loading,
    filtering, adding, editing, and deleting players. It uses a CSV-based
    data access object for persistence.

    Attributes
    ----------
    view : PlayerListView
        The view instance for displaying player data.
    dao : PlayerCsvDAO
        Data access object for player data operations.
    player_edit_view_factory : Callable[[Optional[QDialog], Optional[Player]],
        PlayerEditView] Factory function to create PlayerEditView instances.

    Methods
    -------
    __init__(view, player_edit_view_factory)
        Initialize the controller with view and factory.
    load_players(search_query="")
        Load players into the table, optionally filtered.
    filter_players(text)
        Filter players based on search input and refresh table.
    handle_new_player()
        Open dialog to create a new player.
    handle_edit_player()
        Open dialog to edit selected player.
    delete_player()
        Delete selected player after confirmation.
    show_player_details(player)
        Show details of the selected player in the labels.
    on_table_selection()
        Populate details labels when a table row is selected.
    """

    def __init__(
        self,
        view: "PlayerListView",
        player_edit_view_factory: Callable[
            [Optional[QDialog], Optional[Player]], "PlayerEditView"
        ],
    ) -> None:
        """Initialize the controller with view and factory.

        Sets up the controller with the provided view and factory function
        for creating edit dialogs, and initializes the data access object.

        Parameters
        ----------
        view : PlayerListView
            The view instance for displaying player data.
        player_edit_view_factory : Callable[[Optional[QDialog],
            Optional[Player]], PlayerEditView] Factory function
            to create PlayerEditView instances.

        Returns
        -------
        None
        """
        self.view = view
        self.dao = PlayerCsvDAO()
        self.player_edit_view_factory = player_edit_view_factory

    def load_players(self, search_query: str = "") -> None:
        """Load players into the table, optionally filtered by search query.

        Retrieves players from the DAO, filters them by the search query if
        provided, and updates the view's table with the player data.

        Parameters
        ----------
        search_query : str, optional
            Query to filter players by ID or name. Defaults to "".

        Returns
        -------
        None
        """
        players = self.dao.list()
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
        self.show_player_details(None)

    def filter_players(self, text: str) -> None:
        """Filter players based on search input and refresh table.

        Calls load_players with the provided search text to update the
        table with filtered results.

        Parameters
        ----------
        text : str
            The search text to filter players by ID or name.

        Returns
        -------
        None
        """
        self.load_players(text)

    def handle_new_player(self) -> None:
        """Open dialog to create a new player.

        Opens a dialog for entering new player details, assigns a new ID,
        and inserts the player into the DAO. Displays success or failure
        message based on the result.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        dialog = self.player_edit_view_factory(self.view)
        if dialog.exec():
            data = dialog.controller.get_data()
            player_id = (
                max((player.id for player in self.dao.list()), default=0) + 1
            )
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
                    self.view.tr("Cadastro do jogador realizado com sucesso."),
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    self.view.tr("Falha ao adicionar o jogador."),
                )

    def handle_edit_player(self) -> None:
        """Open dialog to edit selected player.

        Opens a dialog pre-filled with the selected player's data, updates
        the player in the DAO if confirmed, and displays success or failure
        message.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                self.view.tr(
                    "Por favor selecione um jogador na listagem para editar."
                ),
            )
            return
        player_id = int(self.view.table.item(selected[0].row(), 0).text())
        player = self.dao.select(player_id)
        if not player:
            QMessageBox.critical(
                self.view,
                self.view.parent().get_title(),
                self.view.tr("Jogador não encontrado."),
            )
            return
        dialog = self.player_edit_view_factory(self.view, player)
        if dialog.exec() and dialog.controller.ok_clicked:
            data = dialog.controller.get_data()
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
                    self.view.tr("Dados do jogador atualizados."),
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    self.view.tr("Falha ao atualizar os dados do jogador."),
                )

    def delete_player(self) -> None:
        """Delete selected player after confirmation.

        Prompts the user to confirm deletion of the selected player, removes
        the player from the DAO if confirmed, and displays success or failure
        message.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                self.view.tr(
                    "Por favor selecione um jogador na listagem para excluir."
                ),
            )
            return
        player_id = int(self.view.table.item(selected[0].row(), 0).text())
        player_name = self.view.table.item(selected[0].row(), 1).text()
        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.view.parent().windowIcon())
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.view.parent().windowTitle())
        msg_box.setText(
            self.view.tr(f"Confirma a exclusão do jogador?\n{player_name}")
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText(self.view.tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.view.tr("Não"))
        if msg_box.exec() == QMessageBox.Yes:
            result = self.dao.delete(player_id)
            if result:
                self.load_players(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    self.view.tr("Jogador excluído com sucesso."),
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    self.view.tr("Não foi possível excluir o jogador."),
                )

    def show_player_details(self, player: Optional[Player]) -> None:
        """Show details of the selected player in the labels.

        Updates the view's labels with the selected player's details or
        clears them if no player is provided.

        Parameters
        ----------
        player : Optional[Player]
            The player whose details are to be displayed, or None to clear.

        Returns
        -------
        None
        """
        if player:
            self.view.id_label.setText(str(player.id))
            self.view.name_label.setText(player.name)
            mask = AppConfig.get_geral_date_mask()
            self.view.birth_date_label.setText(
                # player.birth_date.strftime("%Y-%m-%d")
                player.birth_date.strftime(mask)
            )
            self.view.observation_label.setText(player.observation)
        else:
            self.view.id_label.setText("")
            self.view.name_label.setText("")
            self.view.birth_date_label.setText("")
            self.view.observation_label.setText("")

    def on_table_selection(self) -> None:
        """Populate details labels when a table row is selected.

        Retrieves the selected player's data from the DAO and updates the
        view's labels with the player's details, or clears them if no player
        is selected.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        selected = self.view.table.selectedItems()
        if selected:
            player_id = int(self.view.table.item(selected[0].row(), 0).text())
            player = self.dao.select(player_id)
            self.show_player_details(player)
        else:
            self.show_player_details(None)
