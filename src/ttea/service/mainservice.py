"""Global service of the main window (exit and other global actions)."""

from typing import TYPE_CHECKING

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from ttea.model import AppModel
    from ttea.util import MessageService


class MainService:
    """Global service of the main application.

    Parameters
    ----------
    model : AppModel
        Global application state.
    message_service : MessageService
        Service used to show dialogs.

    Attributes
    ----------
    model : AppModel
        Global application state.
    msg : MessageService
        Service used to show dialogs.
    """

    def __init__(self, model: "AppModel", message_service: "MessageService"):
        self.model = model
        self.msg = message_service

    def confirm_exit(self) -> bool:
        """Ask the user to confirm leaving the application.

        Returns
        -------
        bool
            True if the user answered "Yes"; "No" is the default button.

        Notes
        -----
        The question and title (pt_BR source texts) are translated at
        runtime with ``QCoreApplication.translate`` in the
        ``"MainService"`` context.
        """
        return self.msg.question(
            text=QCoreApplication.translate(
                "MainService", "Deseja sair do sistema?"
            ),
            title=QCoreApplication.translate(
                "MainService", "Plataforma T-TEA"
            ),
            default_no=True,
        )

    def quit_application(self) -> None:
        """Quit the Qt application."""
        QApplication.quit()
