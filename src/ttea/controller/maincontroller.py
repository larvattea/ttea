"""Controller of the main window: menus, dialogs and exit."""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject

from ttea.controller.helpcontroller import HelpController
from ttea.service import MainService

if TYPE_CHECKING:
    from ttea.model import AppModel
    from ttea.util import MessageService
    from ttea.view.mainview import MainView


class MainController(QObject):
    """Controller of the main window.

    Opens the dialogs of the menus, the game actions and the help, and
    handles the application exit.

    Parameters
    ----------
    view : MainView
        The main window; it is also the parent of the controller.
    model : AppModel
        Global application state.
    message_service : MessageService
        Service used to show dialogs.

    Attributes
    ----------
    view : MainView
        The main window.
    model : AppModel
        Global application state.
    message_service : MessageService
        Service used to show dialogs.
    app_service : MainService
        Global service (exit confirmation).
    app_factory : AppViewFactory
        Factory of the application views.
    """

    def __init__(
        self,
        view: "MainView",
        model: "AppModel",
        message_service: "MessageService",
    ):
        from ttea.factory import ViewFactory

        super().__init__(parent=view)
        self.view = view
        self.model = model
        self.message_service = message_service

        self.app_service = MainService(
            model=model, message_service=message_service
        )

        self.app_factory = ViewFactory.get_app_view_factory()

        self._is_quitting = False

    # ------------------------------------------------------------------
    def handle_exit(self) -> None:
        """Ask for confirmation and quit the application.

        Does nothing if the application is already quitting.
        """
        if self._is_quitting:
            return  # already quitting

        if self.app_service.confirm_exit():
            self._is_quitting = True
            self.app_service.quit_application()

    def try_close(self) -> bool:
        """Ask for confirmation and quit when the window is closed.

        Returns
        -------
        bool
            True if the application is quitting (the close event can be
            accepted), False if the user cancelled.
        """
        if self._is_quitting:
            return True
        if self.app_service.confirm_exit():
            self._is_quitting = True
            self.app_service.quit_application()
            return True
        return False

    def open_player_list(self) -> None:
        """Open the player list dialog (modal)."""
        dialog = self.app_factory.create_player_list_view(
            self.view,
            self.app_factory.create_player_edit_view,
        )
        dialog.exec()

    def open_professional_list(self) -> None:
        """Open the professional list dialog (modal)."""
        dialog = self.app_factory.create_professional_list_view(
            self.view,
            self.app_factory.create_professional_edit_view,
        )
        dialog.exec()

    def open_institutionfacility_list(self) -> None:
        """Open the institution/facility list dialog (modal)."""
        dialog = self.app_factory.create_institutionfacility_list_view(
            self.view,
            self.app_factory.create_institutionfacility_edit_view,
        )
        dialog.exec()

    def open_calibration(self) -> None:
        """Open the calibration dialog (modal)."""
        dialog = self.app_factory.create_calibration_view(parent=self.view)
        dialog.exec()

    def open_calibration_setting(self) -> None:
        """Open the calibration settings dialog (modal)."""
        dialog = self.app_factory.create_calibrationsetting_view(
            parent=self.view
        )
        dialog.exec()

    def open_game_action(
        self, game_name: str, method: str, edit_method: Optional[str] = None
    ) -> None:
        """Open a dialog provided by a game's view factory.

        Parameters
        ----------
        game_name : str
            Game ID registered in ``ViewFactory``.
        method : str
            Name of the factory method that creates the dialog.
        edit_method : str | None, optional
            Name of the factory method that creates the edit dialog,
            passed to the first one when the factory has it. Default is
            None.

        Raises
        ------
        KeyError
            If no view factory is loaded for ``game_name``.
        AttributeError
            If the factory has no ``method``.
        """
        from ttea.factory import ViewFactory

        factory = ViewFactory.get_game_view_factory(game_name)
        view_creator = getattr(factory, method)

        if edit_method and hasattr(factory, edit_method):
            edit_creator = getattr(factory, edit_method)
            dialog = view_creator(self.view, edit_creator)
        else:
            dialog = view_creator(self.view)

        dialog.exec()

    def open_help(self) -> None:
        """Open the help at the topic of the active screen."""
        HelpController.instance().show_help()

    def open_language(self) -> None:
        """Open the language dialog and retranslate the main window."""
        dialog = self.app_factory.create_language_view(parent=self.view)
        dialog.exec()

        if hasattr(self.view, "retranslateUi"):
            self.view.retranslateUi(self.view)
            self.view.setup_status_bar()

    def open_about(self) -> None:
        """Open the about dialog (modal)."""
        dialog = self.app_factory.create_about_view(parent=self.view)
        dialog.exec()

    def open_playergamelaunch(self) -> None:
        """Open the game launch dialog (modal)."""
        dialog = self.app_factory.create_playergamelauch_view(parent=self.view)
        dialog.exec()
