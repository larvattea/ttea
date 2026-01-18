from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from udescjoinvilletteagames.kartea.model import PlayerKarteaConfig
from udescjoinvilletteagames.kartea.service import (
    PlayerKarteaConfigService,
)  # New import

if TYPE_CHECKING:
    from udescjoinvilletteagames.kartea.view import (
        PlayerKarteaConfigEditView,
        PlayerKarteaConfigListView,
    )


class PlayerKarteaConfigListController:
    def __init__(
        self,
        view: "PlayerKarteaConfigListView",
        player_kartea_config_edit_view_factory: Callable[
            [Optional[QDialog], Optional[PlayerKarteaConfig]],
            "PlayerKarteaConfigEditView",
        ],
    ) -> None:
        self.view = view
        self.service = (
            PlayerKarteaConfigService()
        )  # Use Service instead of DAO
        self.player_kartea_config_edit_view_factory = (
            player_kartea_config_edit_view_factory
        )

    def load_configs(self, search_query: str = "") -> None:
        configs = self.service.search_configs(
            search_query
        )  # Use service search
        self.view.tbl_config.setRowCount(0)
        for config in configs:
            row = self.view.tbl_config.rowCount()
            self.view.tbl_config.insertRow(row)
            self.view.tbl_config.setItem(
                row, 0, QTableWidgetItem(str(config.player.id))
            )
            self.view.tbl_config.setItem(
                row, 1, QTableWidgetItem(config.player.name)
            )
        self.show_config_details(None)

    def filter_configs(self) -> None:
        self.load_configs(self.view.led_search.text())

    def handle_new_config(self) -> None:
        edit_view = self.player_kartea_config_edit_view_factory(
            self.view, None
        )
        if edit_view.exec():
            data = (
                edit_view.controller.get_data()
            )  # Assume EditView has a get_data() method
            new_config = self.service.create_config(data)
            if new_config:
                self.load_configs(self.view.led_search.text())
                # Select the new row, etc.

    def handle_edit_config(self) -> None:
        selected = self.view.tbl_config.selectedItems()
        if not selected:
            QMessageBox.warning(self.view, "Warning", "Select a config")
            return
        player_id = int(self.view.tbl_config.item(selected[0].row(), 0).text())
        config = self.service.find_by_player_id(player_id)
        if config:
            edit_view = self.player_kartea_config_edit_view_factory(
                self.view, config
            )
            if edit_view.exec():
                data = edit_view.get_data()
                if self.service.update_config(player_id, data):
                    self.load_configs(self.view.led_search.text())

    def delete_config(self) -> None:
        selected = self.view.tbl_config.selectedItems()
        if not selected:
            QMessageBox.warning(self.view, "Warning", "Select a config")
            return
        player_id = int(self.view.tbl_config.item(selected[0].row(), 0).text())
        if (
            QMessageBox.question(self.view, "Confirm", "Delete?")
            == QMessageBox.Yes
        ):
            if self.service.delete_config(player_id):
                self.load_configs(self.view.led_search.text())

    def show_config_details(
        self, config: Optional[PlayerKarteaConfig]
    ) -> None:
        if config:
            self.view.lbl_id_value.setText(str(config.player.id))
            self.view.lbl_name_value.setText(config.player.name)
            self.view.lbl_phase_value.setText(str(config.phase.id))
            self.view.lbl_level_value.setText(str(config.level.id))
            self.view.lbl_time_value.setText(str(config.level_time))
        else:
            self.view.lbl_id_value.setText("")
            self.view.lbl_name_value.setText("")
            self.view.lbl_phase_value.setText("")
            self.view.lbl_level_value.setText("")
            self.view.lbl_time_value.setText("")

    def on_table_selection(self) -> None:
        selected = self.view.tbl_config.selectedItems()
        if selected:
            player_id = int(
                self.view.tbl_config.item(selected[0].row(), 0).text()
            )
            config = self.service.find_by_player_id(player_id)
            self.show_config_details(config)
        else:
            self.show_config_details(None)
