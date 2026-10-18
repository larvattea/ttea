"""Controller of the player Kartea configuration list screen."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.games.kartea.model import PlayerKarteaConfig
    from ttea.games.kartea.service import PlayerKarteaConfigService
    from ttea.games.kartea.view import (
        PlayerKarteaConfigEditView,
        PlayerKarteaConfigListView,
    )


class PlayerKarteaConfigListController(QObject):
    """Orchestrate PlayerKarteaConfigListView and the config service.

    Lightweight controller that follows the MVCS pattern: mediates
    between view and service layer, handling user interactions and
    updating the UI accordingly.

    Parameters
    ----------
    view : PlayerKarteaConfigListView
        The main list view instance to control.
    player_kartea_config_edit_view_factory : Callable
        Function that returns a ``PlayerKarteaConfigEditView`` dialog.
        Signature: ``(parent_view, config) ->
        PlayerKarteaConfigEditView``.
    service : PlayerKarteaConfigService
        Shared service (injected by the view factory).

    Attributes
    ----------
    view : PlayerKarteaConfigListView
        Main view displaying the list and details of configs.
    factory : Callable
        Factory function that creates a ``PlayerKarteaConfigEditView``
        dialog, receiving the parent view and an optional config to
        edit.
    service : PlayerKarteaConfigService
        Business logic layer for config CRUD operations.
    msg : MessageService
        Helper for showing info, warning, and error messages.

    Methods
    -------
    load_configs(search_query="")
        Load and display configs, optionally filtered by search term.
    filter_configs(text)
        Filter the config list based on the search input text.
    on_table_selection()
        Update the details panel when a table row is selected.
    select_and_show_config(player_id)
        Select a config row and show its details.
    handle_new_config()
        Open the dialog to create a new config.
    handle_edit_config()
        Open the dialog to edit the selected config.
    delete_config()
        Delete the selected config after confirmation.

    Notes
    -----
    User messages are translated with ``self.tr()`` in the
    "PlayerKarteaConfigListController" context (i18n).
    """

    def __init__(
        self,
        view: "PlayerKarteaConfigListView",
        player_kartea_config_edit_view_factory: Callable[
            [QDialog | None, "PlayerKarteaConfig | None"],
            "PlayerKarteaConfigEditView",
        ],
        service: "PlayerKarteaConfigService",
    ) -> None:
        super().__init__()
        self.view = view
        self.factory = player_kartea_config_edit_view_factory
        self.service = service
        self.msg = MessageService(view)

    def load_configs(self, search_query: str = "") -> None:
        """Load player configs from the service and fill the table view.

        Parameters
        ----------
        search_query : str, optional
            Search term to filter configs by player name or ID (default
            is an empty string, which lists all).

        Notes
        -----
        The details panel is cleared.
        """
        configs = self.service.search_configs(search_query)
        self.view.populate_table(configs)
        self.view.clear_details()

    def filter_configs(self, text: str) -> None:
        """Filter the player config list based on the search input text.

        Parameters
        ----------
        text : str
            Search text; surrounding spaces are ignored.
        """
        self.load_configs(text.strip())

    def on_table_selection(self) -> None:
        """Update the details pane for the selected config.

        Clears the details when no row is selected.
        """
        player_id = self.view.get_selected_player_id()
        if player_id is not None:
            config = self.service.find_config_by_player_id(player_id)
            self.view.display_config_details(config)
        else:
            self.view.clear_details()

    def select_and_show_config(self, player_id: int) -> None:
        """Select a player config row by ID and display its details.

        Parameters
        ----------
        player_id : int
            The ID of the player whose config is selected and shown.
            Nothing happens if the player has no config.
        """
        config = self.service.find_config_by_player_id(player_id)
        if config:
            self.view.display_config_details(config)
            self.view.select_row_by_id(player_id)

    def handle_new_config(self) -> None:
        """Open the dialog for a new config and save it if accepted.

        Notes
        -----
        On success the list is reloaded with the current search, the new
        config is selected and a confirmation is shown; on failure, an
        error message.
        """
        dialog = self.factory(self.view, None)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        config = self.service.create_config(data)
        if config:
            self.load_configs(self.view.get_search_text())
            self.select_and_show_config(config.player.id)
            self.msg.info(self.tr("Configuração cadastrada com sucesso!"))
        else:
            self.msg.critical(self.tr("Erro ao salvar configuração."))

    def handle_edit_config(self) -> None:
        """Edit the selected config in a dialog and save if accepted.

        Notes
        -----
        Warns when no row is selected and shows an error if the config
        no longer exists. On success the list is reloaded and the config
        is selected again.
        """
        player_id = self.view.get_selected_player_id()
        if not player_id:
            self.msg.warning(
                self.tr("Selecione uma configuração para editar.")
            )
            return

        config = self.service.find_config_by_player_id(player_id)
        if not config:
            self.msg.critical(self.tr("Configuração não encontrada."))
            return

        dialog = self.factory(self.view, config)
        if not dialog.exec():
            return

        data = dialog.controller.get_data()
        if self.service.update_config(player_id, data):
            self.load_configs(self.view.get_search_text())
            self.select_and_show_config(player_id)
            self.msg.info(self.tr("Configuração atualizada com sucesso."))
        else:
            self.msg.critical(self.tr("Erro ao atualizar configuração."))

    def delete_config(self) -> None:
        """Delete the selected player config after user confirmation.

        Notes
        -----
        Warns when no row is selected; does nothing if the config no
        longer exists. After deleting, the list is reloaded and the
        details are cleared.
        """
        player_id = self.view.get_selected_player_id()
        if not player_id:
            self.msg.warning(
                self.tr("Selecione uma configuração para excluir.")
            )
            return

        config = self.service.find_config_by_player_id(player_id)
        if not config:
            return

        if self.msg.question(
            self.tr(
                "Tem certeza que deseja excluir a configuração do jogador?\n{0}"
            ).format(config.player.name)
        ):
            if self.service.delete_config(player_id):
                self.load_configs(self.view.get_search_text())
                self.view.clear_details()
                self.msg.info(self.tr("Configuração excluída com sucesso."))
            else:
                self.msg.critical(self.tr("Erro ao excluir configuração."))
