from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from udescjoinvilletteagames.kartea.dao.config import PlayerKarteaConfigCsvDAO
from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.view import (
        PlayerKarteaConfigEditView,
        PlayerKarteaConfigListView,
    )


class PlayerKarteaConfigListController:
    """Controller to handle UI interactions and business logic for player Kartea configuration list.

    Parameters
    ----------
    view : PlayerKarteaConfigListView
        The view instance for displaying player Kartea configuration data.
    player_kartea_config_edit_view_factory : Callable[[Optional[QDialog], Optional[PlayerKarteaConfig]], PlayerKarteaConfigEditView]
        Factory function to create PlayerKarteaConfigEditView instances.

    Attributes
    ----------
    view : PlayerKarteaConfigListView
        The view instance for displaying player Kartea configuration data.
    dao : PlayerKarteaConfigCsvDAO
        Data access object for player Kartea configuration data operations.
    player_kartea_config_edit_view_factory : Callable[[Optional[QDialog], Optional[PlayerKarteaConfig]], PlayerKarteaConfigEditView]
        Factory function to create PlayerKarteaConfigEditView instances.

    Methods
    -------
    load_configs(search_query: str = "") -> None
        Load configurations into the table, optionally filtered by search query.
    filter_configs() -> None
        Filter configurations based on search input and refresh table.
    handle_new_config() -> None
        Open dialog to create a new configuration.
    handle_edit_config() -> None
        Open dialog to edit selected configuration.
    delete_config() -> None
        Delete selected configuration.
    show_config_details(config: Optional[PlayerKarteaConfig]) -> None
        Show details of the selected configuration in the labels.
    on_table_selection() -> None
        Populate details labels when a table row is selected.
    """

    def __init__(
        self,
        view: "PlayerKarteaConfigListView",
        player_kartea_config_edit_view_factory: Callable[
            [Optional[QDialog], Optional[PlayerKarteaConfig]],
            "PlayerKarteaConfigEditView",
        ],
    ) -> None:
        """Initialize the controller with a view and a factory for PlayerKarteaConfigEditView.

        Parameters
        ----------
        view : PlayerKarteaConfigListView
            The view instance for displaying player Kartea configuration data.
        player_kartea_config_edit_view_factory : Callable[[Optional[QDialog], Optional[PlayerKarteaConfig]], PlayerKarteaConfigEditView]
            Factory function to create PlayerKarteaConfigEditView instances.

        Returns
        -------
        None
        """
        self.view = view
        self.dao = PlayerKarteaConfigCsvDAO()
        self.player_kartea_config_edit_view_factory = (
            player_kartea_config_edit_view_factory
        )

    def load_configs(self, search_query: str = "") -> None:
        """Load configurations into the table, optionally filtered by search query.

        Parameters
        ----------
        search_query : str, optional
            Query to filter configurations by player name or ID (default is "").

        Returns
        -------
        None

        Notes
        -----
        - Filters configurations if search_query is provided, matching against player ID or name.
        - Updates the table with filtered or all configurations.
        - Clears configuration details display when reloading.
        """
        configs = self.dao.list()

        # Filter configurations by player name or ID if search_query is provided
        if search_query:
            search_query = search_query.lower()
            configs = [
                config
                for config in configs
                if (
                    search_query in str(config.player.id)
                    or search_query in config.player.name.lower()
                )
            ]
        self.view.table.setRowCount(len(configs))
        for row, config in enumerate(configs):
            self.view.table.setItem(
                row, 0, QTableWidgetItem(str(config.player.id))
            )
            self.view.table.setItem(
                row, 1, QTableWidgetItem(config.player.name)
            )

        # Clear details when reloading configurations
        self.show_config_details(None)

    def filter_configs(self) -> None:
        """Filter configurations based on search input and refresh table.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves the search query from the view's search input.
        - Calls load_configs with the search query to update the table.
        """
        search_query = self.view.search_input.text()
        self.load_configs(search_query)

    def handle_new_config(self) -> None:
        """Open dialog to create a new configuration.

        Returns
        -------
        None

        Notes
        -----
        - Creates a new configuration dialog using the factory.
        - Inserts new configuration into the database if dialog is accepted.
        - Displays success or failure message based on insertion result.
        - Reloads the configuration list after successful insertion.
        """
        dialog = self.player_kartea_config_edit_view_factory(
            self.view, None
        )  # Factory creates view with controller
        if dialog.exec():
            data = dialog.controller.get_data()
            config = PlayerKarteaConfig(**data)
            result = self.dao.insert(config)
            if result:
                self.load_configs(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Configuração adicionada com sucesso.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Falha ao adicionar a configuração.",
                )

    def handle_edit_config(self) -> None:
        """Open dialog to edit selected configuration.

        Returns
        -------
        None

        Notes
        -----
        - Checks if a configuration is selected; shows warning if not.
        - Retrieves selected configuration's data and opens edit dialog.
        - Updates configuration data if dialog is accepted and saves changes.
        - Displays success or failure message based on update result.
        - Reloads the configuration list after successful update.
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                "Por favor selecione uma configuração para editar.",
            )
            return
        player_id = int(self.view.table.item(selected[0].row(), 0).text())
        config = self.dao.select(player_id)
        if not config:
            QMessageBox.critical(
                self.view, "Erro", "Configuração não encontrada."
            )
            return
        dialog = self.player_kartea_config_edit_view_factory(
            self.view, config
        )  # Factory creates view with controller
        if dialog.exec() and dialog.controller.ok_clicked:
            data = (
                dialog.controller.get_data()
            )  # Use get_config_data (corrected from get_player_kartea_data)
            updated_config = PlayerKarteaConfig(**data)
            result = self.dao.update(updated_config)
            if result:
                self.load_configs(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Dados da configuração atualizados.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Falha ao atualizar os dados da configuração.",
                )

    def delete_config(self) -> None:
        """Delete selected configuration.

        Returns
        -------
        None

        Notes
        -----
        - Checks if a configuration is selected; shows warning if not.
        - Prompts user to confirm deletion with player name.
        - Deletes configuration if confirmed and displays success or failure message.
        - Reloads the configuration list after successful deletion.
        """
        selected = self.view.table.selectedItems()
        if not selected:
            QMessageBox.warning(
                self.view,
                self.view.parent().get_title(),
                "Por favor selecione uma configuração para excluir.",
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
                f"Confirma a exclusão da configuração do jogador?\n{player_name}"
            )
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText(self.view.parent().tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.view.parent().tr("Não"))
        if msg_box.exec() == QMessageBox.Yes:
            result = self.dao.delete(player_id)
            if result:
                self.load_configs(self.view.search_input.text())
                QMessageBox.information(
                    self.view,
                    self.view.parent().get_title(),
                    "Configuração excluída com sucesso.",
                )
            else:
                QMessageBox.critical(
                    self.view,
                    self.view.parent().get_title(),
                    "Não foi possível excluir a configuração.",
                )

    def show_config_details(
        self, config: Optional[PlayerKarteaConfig]
    ) -> None:
        """Show details of the selected configuration in the labels.

        Parameters
        ----------
        config : Optional[PlayerKarteaConfig]
            The configuration object to display details for, or None to clear.

        Returns
        -------
        None

        Notes
        -----
        - Displays player ID, name, current phase, current level, and level time in view labels.
        - Clears labels if no configuration is provided.
        """
        if config:
            self.view.id_label.setText(str(config.player.id))
            self.view.name_label.setText(config.player.name)
            self.view.current_phase_label.setText(str(config.phase.id))
            self.view.current_level_label.setText(str(config.level.id))
            self.view.level_time_label.setText(str(config.level_time))
        else:
            self.view.id_label.setText("")
            self.view.name_label.setText("")
            self.view.current_phase_label.setText("")
            self.view.current_level_label.setText("")
            self.view.level_time_label.setText("")

    def on_table_selection(self) -> None:
        """Populate details labels when a table row is selected.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves selected configuration's player ID from the table.
        - Fetches configuration data and updates details labels via show_config_details.
        - Clears details if no row is selected.
        """
        selected = self.view.table.selectedItems()
        if selected:
            player_id = int(self.view.table.item(selected[0].row(), 0).text())
            config = self.dao.select(player_id)
            self.show_config_details(config)
        else:
            self.show_config_details(None)
