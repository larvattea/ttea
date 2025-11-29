from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QWidget


class MessageService:
    """
    Centralized service for displaying user messages.

    Provides a clean, translatable, and testable interface for showing
    information, warnings, errors, and confirmation dialogs. Follows
    Qt's QMessageBox signature: text first, title optional.

    Attributes
    ----------
    parent : QWidget
        The widget used as parent for all dialogs.
    title : str
        Default window title obtained from the main window.
    tr : callable
        Translation function (parent.tr) for localized strings.

    Methods
    -------
    __init__(parent)
        Initialize the message service.
    info(text, title=None)
        Show an information message dialog.
    warning(text, title=None)
        Show a warning message dialog.
    critical(text, title=None)
        Show a critical error message dialog.
    question(text, title=None, default_no=True)
        Show a Yes/No question dialog with translated buttons.

    Examples
    --------
    >>> msg = MessageService(self)
    >>> msg.info("Operation completed successfully!")
    >>> if msg.question("Delete this item?", "Confirm"):
    ...     delete_item()
    """

    def __init__(self, parent: QWidget):
        """
        Initialize the message service.

        Parameters
        ----------
        parent : QWidget
            Parent widget used for dialog ownership and translation.
        """
        self.parent = parent

        # Climb to main window to get proper title
        main_window = parent
        while main_window.parent() is not None:
            main_window = main_window.parent()
        self.title = main_window.windowTitle()

        # Use parent's translation context
        self.tr = parent.tr

    def info(self, text: str, title: Optional[str] = None) -> None:
        """
        Display an information message dialog.

        Parameters
        ----------
        text : str
            The message body to display.
        title : str, optional
            Dialog title. Uses main window title if not provided.

        Returns
        -------
        None
        """
        QMessageBox.information(self.parent, title or self.title, text)

    def warning(self, text: str, title: Optional[str] = None) -> None:
        """
        Display a warning message dialog.

        Parameters
        ----------
        text : str
            The warning message to display.
        title : str, optional
            Dialog title. Uses main window title if not provided.

        Returns
        -------
        None
        """
        QMessageBox.warning(self.parent, title or self.title, text)

    def critical(self, text: str, title: Optional[str] = None) -> None:
        """
        Display a critical error message dialog.

        Parameters
        ----------
        text : str
            The error message to display.
        title : str, optional
            Dialog title. Uses main window title if not provided.

        Returns
        -------
        None
        """
        QMessageBox.critical(self.parent, title or self.title, text)

    def question(
        self,
        text: str,
        title: Optional[str] = None,
        default_no: bool = True,
    ) -> bool:
        """
        Display a Yes/No question dialog with translated buttons.

        Parameters
        ----------
        text : str
            The question text to display.
        title : str, optional
            Dialog title. Uses main window title if not provided.
        default_no : bool, default True
            If True, "No" is the default button; otherwise "Yes".

        Returns
        -------
        bool
            True if user clicked "Yes" (Sim), False if "No" (Não).
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title or self.title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(
            QMessageBox.No if default_no else QMessageBox.Yes
        )

        # Translated buttons
        yes_btn = msg_box.button(QMessageBox.Yes)
        no_btn = msg_box.button(QMessageBox.No)
        yes_btn.setText(self.tr("Sim"))
        no_btn.setText(self.tr("Não"))

        return msg_box.exec() == QMessageBox.Yes
