# udescjoinvillettea/controller/maincontroller.py
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

from udescjoinvilletteaservice import MainService
from udescjoinvilletteautil import PathConfig

if TYPE_CHECKING:
    from udescjoinvilletteamodel import AppModel
    from udescjoinvilletteautil import MessageService
    from udescjoinvilletteaview.mainview import \
        MainView  # Apenas para type hint


class MainController(QObject):
    def __init__(
        self,
        view: "MainView",
        model: "AppModel",
        message_service: "MessageService",
    ):
        from udescjoinvilletteafactory import ViewFactory

        super().__init__(parent=view)
        self.view = view
        self.model = model
        self.message_service = message_service

        # Serviço principal (recebe MessageService injetado)
        self.app_service = MainService(
            model=model, message_service=message_service
        )

        # Factories
        self.app_factory = ViewFactory.get_app_view_factory()
        self.kartea_factory = ViewFactory.get_kartea_view_factory()

        self._load_games_menu()  # já ordena uma única vez aqui
        self._is_quitting = False

    def _load_games_menu(self) -> None:
        games = []
        for game_dir in PathConfig.path_games():
            display_name = (
                game_dir.replace("tea", "TEA").replace("_", " ").title()
            )

            icon_name = (
                "kartea4.ico" if "kartea" in game_dir.lower() else "game.png"
            )
            icon_path = PathConfig.icon_system(icon_name)

            games.append((display_name, icon_path))

        games.sort(key=lambda x: x[0])  # ordena apenas uma vez
        self.view.populate_games_menu(games)  # View não ordena mais

    # ------------------------------------------------------------------
    def handle_exit(self) -> None:
        if self._is_quitting:
            return  # já estamos saindo, não faz nada

        if self.app_service.confirm_exit():
            self._is_quitting = True
            self.app_service.quit_application()

    def try_close(self) -> bool:
        if self._is_quitting:
            return True
        if self.app_service.confirm_exit():
            self._is_quitting = True
            self.app_service.quit_application()
            return True
        return False

    def open_player_list(self) -> None:
        dialog = self.app_factory.create_player_list_view(
            self.view,
            self.app_factory.create_player_edit_view,
        )
        dialog.exec()

    def open_kartea_player_config(self) -> None:
        dialog = self.kartea_factory.create_player_kartea_config_list_view(
            self.view,
            self.kartea_factory.create_player_kartea_config_edit_view,
        )
        dialog.exec()

    def open_calibration(self) -> None:
        self.view.update_status_message(
            self.tr("Funcionalidade de calibração em desenvolvimento...")
        )

    def open_help(self) -> None:
        try:
            # open_help()
            pass
        except Exception as e:
            self.view.show_critical_error(
                self.tr("Erro ao abrir ajuda."), str(e)
            )

    def open_about(self) -> None:
        dialog = self.app_factory.create_about_view(parent=self.view)
        dialog.exec()

    def start_game(self, game_name: str) -> None:
        try:
            if "KarTEA" in game_name:
                from udescjoinvillettea.games.kartea.main import launch_kartea

                launch_kartea(parent=self.view)
            else:
                self.view.update_status_message(
                    self.tr("Jogo '{}' não implementado ainda.").format(
                        game_name
                    )
                )
        except Exception as e:
            self.view.show_critical_error(
                self.tr("Erro ao iniciar jogo"),
                self.tr("{} não pôde ser iniciado:\n{}").format(
                    game_name, str(e)
                ),
            )
