"""Centralized Qt message dialog service.

This module provides the ``MessageService`` class for showing
information, warning, critical and question dialogs in a Qt
application.
"""

from typing import Optional

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox, QWidget


class MessageService:
    """Centralized service for displaying user messages.

    Provides a clean, translatable and testable interface for showing
    information, warnings, errors and confirmation dialogs. Follows
    Qt's QMessageBox signature: text first, title optional.

    Parameters
    ----------
    parent : QWidget
        Parent widget of the dialogs.

    Attributes
    ----------
    parent : QWidget
        The widget used as parent for all dialogs.
    title : str
        Default dialog title: the window title of the top-level
        ancestor of ``parent``, read when the service is created.

    Methods
    -------
    info(text, title=None)
        Show an information message dialog.
    warning(text, title=None)
        Show a warning message dialog.
    critical(text, title=None)
        Show a critical error message dialog.
    question(text, title=None, default_no=True)
        Show a Yes/No question dialog with translated buttons.
    critical_global(text, title=None)
        Show a critical dialog when no parent widget is available.

    Notes
    -----
    The texts are shown as given, so callers pass already translated
    strings. Only the Yes/No button labels of ``question`` are
    translated here.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent

        main_window = parent
        while main_window.parent() is not None:
            main_window = main_window.parent()
        self.title = main_window.windowTitle()

    def info(self, text: str, title: Optional[str] = None) -> None:
        """Display an information message dialog.

        Parameters
        ----------
        text : str
            The message body to display.
        title : str | None, optional
            Dialog title. Default is None, which uses ``title``.
        """
        QMessageBox.information(self.parent, title or self.title, text)

    def warning(self, text: str, title: Optional[str] = None) -> None:
        """Display a warning message dialog.

        Parameters
        ----------
        text : str
            The warning message to display.
        title : str | None, optional
            Dialog title. Default is None, which uses ``title``.
        """
        QMessageBox.warning(self.parent, title or self.title, text)

    def critical(self, text: str, title: Optional[str] = None) -> None:
        """Display a critical error message dialog.

        Parameters
        ----------
        text : str
            The error message to display.
        title : str | None, optional
            Dialog title. Default is None, which uses ``title``.
        """
        QMessageBox.critical(self.parent, title or self.title, text)

    def question(
        self,
        text: str,
        title: Optional[str] = None,
        default_no: bool = True,
    ) -> bool:
        """Display a Yes/No question dialog with translated buttons.

        Parameters
        ----------
        text : str
            The question text to display.
        title : str | None, optional
            Dialog title. Default is None, which uses ``title``.
        default_no : bool, optional
            If True, "No" is the default button; otherwise "Yes".
            Default is True.

        Returns
        -------
        bool
            True if the user clicked "Yes", False otherwise (including
            closing the dialog).

        Notes
        -----
        The button labels (pt_BR source texts "Sim" and "Não") are
        translated at runtime with ``QCoreApplication.translate`` in the
        ``"MessageService"`` context, because the standard buttons do
        not take the context of the parent widget.
        """
        # The .ts files hold these labels in the MessageService context.
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title or self.title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(
            QMessageBox.No if default_no else QMessageBox.Yes
        )
        msg_box.button(QMessageBox.Yes).setText(
            QCoreApplication.translate("MessageService", "Sim")
        )
        msg_box.button(QMessageBox.No).setText(
            QCoreApplication.translate("MessageService", "Não")
        )

        return msg_box.exec() == QMessageBox.Yes

    @staticmethod
    def critical_global(text: str, title: Optional[str] = None) -> None:
        """Show a critical dialog when no parent widget is available.

        Parameters
        ----------
        text : str
            The error message to display.
        title : str | None, optional
            Dialog title. Default is None, which uses
            ``AppConfig.get_title()``.

        Notes
        -----
        A temporary hidden QWidget, with the application icon, is
        created as parent of the modal dialog and scheduled for
        deletion afterwards. A QApplication must already exist.
        """
        from ttea.app import AppConfig

        window = QWidget()
        window.setWindowTitle(title or AppConfig.get_title())
        window.setWindowIcon(QIcon(AppConfig.ICON_APP))
        MessageService(window).critical(text)

        window.deleteLater()
