from typing import Callable, Optional

from PySide6.QtCore import QObject

from udescjoinvilletteamodel import Language
from udescjoinvilletteaview import LanguageView


class LanguageController:
    """Controller for managing language selection.

    Attributes
    ----------
    model : Language
        The model handling language data and logic.
    view : LanguageView
        The view responsible for displaying the language selection UI.

    Methods
    -------
    __init__(self, model: Language, language_view_factory: Callable[[Optional[QObject]], LanguageView]) -> None
        Initialize the LanguageController.
    setup_connections(self) -> None:
        Configures connections between View and Controller.
    initialize_view(self) -> None
        Initializes the View with data from the Model.
    handle_confirm(self) -> None
        Processes the confirmation of the selected language.
    handle_close_event(self, event) -> None
        Handles the window close event.
    get_selected_language(self) -> Optional[str]
        Returns the currently selected language.
    get_system_language(self) -> str
        Returns the system's default language.
    """

    def __init__(
        self,
        model: Language,
        language_view_factory: Callable[[Optional[QObject]], LanguageView],
        parent: Optional[QObject] = None,
    ) -> None:
        """Initialize the LanguageController.

        Parameters
        ----------
        model : Language
            The model handling language data.
        language_view_factory : Callable[[Optional[QObject]], LanguageView]
            Factory function to create a LanguageView instance.
        parent : Optional[QObject]
            The parent QObject for the view.

        Returns
        -------
        None

        Notes
        -----
        Sets up connections and initializes the view upon creation.
        """
        self.model = model
        self.view = language_view_factory(parent)
        self.setup_connections()
        self.initialize_view()

    def setup_connections(self) -> None:
        """Configure connections between View and Controller.

        Returns
        -------
        None

        Notes
        -----
        Connects the confirm button click to handle_confirm and sets the
        close event handler.
        """
        self.view.confirm_button.clicked.connect(self.handle_confirm)
        self.view.closeEvent = self.handle_close_event

    def initialize_view(self) -> None:
        """Initialize the View with data from the Model.

        Returns
        -------
        None

        Notes
        -----
        Populates the view with available languages from the model.
        """
        languages = self.model.get_languages()
        self.view.populate_languages(languages)

    def handle_confirm(self) -> None:
        """Process the confirmation of the selected language.

        Returns
        -------
        None

        Notes
        -----
        If a language is selected, updates the model and accepts the view.
        Otherwise, displays a warning.
        """
        selected_language = self.view.get_checked_language()
        if selected_language:
            self.model.set_selected_language(selected_language)
            self.view.accept()
        else:
            self.view.show_warning()

    def handle_close_event(self, event) -> None:
        """Handle the window close event.

        Parameters
        ----------
        event : QCloseEvent
            The close event triggered by the window.

        Returns
        -------
        None

        Notes
        -----
        If a language is selected, updates the model and accepts the event.
        Otherwise, shows a warning and ignores the event.
        """
        selected_language = self.view.get_checked_language()
        if selected_language:
            self.model.set_selected_language(selected_language)
            self.view.accept()
            event.accept()
        else:
            self.view.show_warning()
            event.ignore()

    def get_selected_language(self) -> Optional[str]:
        """Return the currently selected language.

        Returns
        -------
        Optional[str]
            The selected language, or None if no language is selected.
        """
        return self.model.get_selected_language()

    def get_system_language(self) -> str:
        """Return the system's default language.

        Returns
        -------
        str
            The system's default language.
        """
        return self.model.get_system_language()
