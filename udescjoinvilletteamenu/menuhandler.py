import os
import platform
import subprocess
from typing import Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from udescjoinvilletteafactory import ViewFactory

# Local module imports
from udescjoinvilletteautil import PathConfig


class MenuHandler(QObject):
    """Manages menu actions in the application.

    Parameters
    ----------
    parent : QObject
        The parent QObject for this menu handler.

    Attributes
    ----------
    parent : QObject
        The parent QObject instance.
    translator : Optional[QObject]
        Translator object for handling translations.
    is_exiting : bool
        Flag to prevent duplicate exit calls.

    Methods
    -------
    __init__(parent: QObject) -> None
        Initialize the MenuHandler with a parent QObject.
    do_nothing() -> None
        Display a placeholder dialog with a button.
    menu_exit(event: Optional[QCloseEvent] = None) -> None
        Handle the application exit process.
    menu_player() -> None
        Open the player selection dialog.
    menu_help() -> None
        Open the Qt Assistant with the help file.
    menu_about() -> None
        Display the about dialog.
    """

    def __init__(self, parent: QObject) -> None:
        """Initialize the MenuHandler with a parent QObject.

        Parameters
        ----------
        parent : QObject
            The parent QObject for this menu handler.

        Notes
        -----
        Sets up a shortcut for the F1 key to trigger the help menu.
        """
        super().__init__(parent)
        self.parent = parent
        self.translator = (
            parent.translator if hasattr(parent, "translator") else None
        )
        # Flag to avoid duplicate calls
        self.is_exiting = False

        # Setup F1 shortcut for help
        help_shortcut = QShortcut(QKeySequence(Qt.Key_F1), self.parent)
        help_shortcut.activated.connect(self.menu_help)

    def do_nothing(self) -> None:
        """Display a placeholder dialog with a button.

        Notes
        -----
        Creates a modal QDialog with a single button for testing purposes.
        """
        # Use QDialog and pass the parent
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Placeholder")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(QPushButton("Do nothing button"))
        # Run as modal
        dialog.exec()

    def menu_exit(self, event: Optional[QCloseEvent] = None) -> None:
        """Handle the application exit process.

        Parameters
        ----------
        event : Optional[QCloseEvent], optional
            The close event, if triggered by a window close action.

        Notes
        -----
        Displays a confirmation dialog before exiting the application.
        If the user confirms, the application quits or accepts the close event.
        Prevents duplicate exit calls using the `is_exiting` flag.
        """
        # Check if it is already in the process of leaving to avoid duplication
        if self.is_exiting:
            if event is not None:
                event.accept()
            return
        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.parent.windowIcon())
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.parent.windowTitle())
        # Use self.tr
        msg_box.setText(self.tr("Deseja sair do sistema?"))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # Translate the buttons
        # Use self.tr
        msg_box.button(QMessageBox.Yes).setText(self.tr("Sim"))
        msg_box.button(QMessageBox.No).setText(self.tr("Não"))
        response = msg_box.exec()
        if response == QMessageBox.Yes:
            # Set the flag to indicate exiting
            self.is_exiting = True
            # If it is a window close event
            if event is not None:
                event.accept()
            else:
                # If called from the menu
                QApplication.quit()
        elif event is not None:
            # Just ignore if it's a window event
            event.ignore()

    def menu_player(self) -> None:
        """Open the player selection dialog.

        Notes
        -----
        Creates and displays a modal player selection dialog using ViewFactory.
        """
        # Pass the parent (main window)
        player_list = ViewFactory.create_player_list_view(
            self.parent,
            player_edit_view_factory=ViewFactory.create_player_edit_view,
        )
        # Run as modal
        player_list.exec()

    def menu_help(self) -> None:
        """Open the Qt Assistant with the help file.

        Raises
        ------
        FileNotFoundError
            If the Qt Assistant or help file is not found.

        Notes
        -----
        Opens the Qt Assistant with a specific help file and namespace.
        The help file path is constructed using PathConfig.
        """
        help_file = "helppt.qhc"
        namespace = "ttea.qt.helppt/help"
        start_page = "index.html"

        # Base path for PySide6
        pyside6_path = os.path.dirname(
            os.path.abspath(__import__("PySide6").__file__)
        )
        assistant_name = (
            "assistant.exe" if platform.system() == "Windows" else "assistant"
        )
        assistant_path = os.path.join(pyside6_path, assistant_name)

        # Check if the assistant exists
        if not os.path.exists(assistant_path):
            raise FileNotFoundError(
                f"Qt Assistant não encontrado em: {assistant_path}"
            )

        # .qhc file path
        help_file_path = os.path.join(
            os.getcwd(), PathConfig.path_help_pt(help_file)
        )
        if not os.path.exists(help_file_path):
            raise FileNotFoundError(
                f"Arquivo de ajuda não encontrado: {help_file_path}"
            )

        # Command to open Qt Assistant with arguments
        command = [
            assistant_path,
            "-collectionFile",
            help_file_path,
            "-showUrl",
            f"qthelp://{namespace}/{start_page}",
        ]

        # Execute the command
        subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def menu_about(self) -> None:
        """Display the about dialog.

        Notes
        -----
        Creates and displays a modal about dialog using ViewFactory.
        """
        # Pass the parent (main window)
        about = ViewFactory.create_about_view(self.parent)
        # Run as modal
        about.exec()
