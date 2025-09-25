import sys
import traceback
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtCore import QSettings, QTimer, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

# Local module import
from udescjoinvilletteaapp import AppConfig, TTeaApp
from udescjoinvilletteacontroller import LanguageController
from udescjoinvilletteafactory import ViewFactory
from udescjoinvillettealog import Log
from udescjoinvilletteamodel import Language
from udescjoinvilletteautil import PathConfig
from udescjoinvilletteaview import SplashScreen


def show_error_message(
    exception: Exception,
    translator: Optional[QTranslator] = None,
) -> None:
    """Display an error message dialog and log the error.

    Parameters
    ----------
    exception : Exception
        The exception to display in the error message.
    translator : Optional[QTranslator], optional
        Translator for the error message, by default None.

    Returns
    -------
    None

    Notes
    -----
    If a translator is provided, the error message is translated.
    The application icon is set from AppConfig.ICON_APP.
    The error message dialog is shown with a critical icon.
    """
    log = Log.get_log()
    error_message = (
        "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
        "Por favor, contate o suporte.\n"
        f"Detalhes do erro: {str(exception)}"
    )
    if translator:
        translated = translator.translate(
            "AppLauncher",
            "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
            "Por favor, contate o suporte.\n"
            "Detalhes do erro: {0}",
        )
        if translated and not translated.isspace():
            error_message = translated.format(str(exception))
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        if translator:
            app.installTranslator(translator)
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(AppConfig.ICON_APP))
        msg.setWindowTitle(getattr(AppConfig, "get_title", lambda: "Error")())
        msg.setIcon(QMessageBox.Critical)
        msg.setText(error_message)
        msg.exec()
    except Exception as e:
        log.log_error(f"Failed to show error message dialog: {str(e)}")


def global_exception_hook(
    exctype: type, value: Exception, traceback_obj: traceback
) -> None:
    """Handle uncaught exceptions globally, log them, and show error dialog.

    Parameters
    ----------
    exctype : type
        The type of the exception.
    value : Exception
        The exception instance.
    traceback_obj : traceback
        The traceback object.

    Returns
    -------
    None

    Notes
    -----
    Logs the exception and its stack trace, attempts to load a default
    translator, displays an error message, and exits the application
    with status code 1.
    """
    log = Log.get_log()
    log.log_error("Untreated global exception")
    log.log_error_with_stack(value, traceback_obj=traceback_obj)
    translator = QTranslator()
    translation_file = Path(
        PathConfig.translation(
            Language.DEFAULT_LANGUAGE + AppConfig.TRANSLATION_EXTENSION
        )
    )
    if translation_file.exists():
        translator.load(str(translation_file))
    else:
        translator = None
    show_error_message(value, translator)
    sys.__excepthook__(exctype, value, traceback_obj)
    sys.exit(1)


sys.excepthook = global_exception_hook


class AppLauncher:
    """Main application launcher for the TTeaApp.

    Manages application initialization, language selection, translation,
    and main window setup.

    Attributes
    ----------
    log : Log
        Logger instance for logging application events.
    app : QApplication
        The Qt application instance.
    translator : QTranslator
        Translator for handling internationalization.
    language_model : Language
        Model for managing supported languages.
    splash : Optional[SplashScreen]
        Splash screen displayed during startup.
    main_window : Optional[TTeaApp]
        Main application window.
    settings : QSettings
        Application configuration settings.
    language_controller : Optional[LanguageController]
        Controller for language selection.
    current_language : str
        The currently selected language code.
    has_error : bool
        Flag indicating if an error has occurred.

    Methods
    -------
    __init__(app: Optional[QApplication] = None,
             settings: Optional[QSettings] = None) -> None
        Initialize the AppLauncher with optional application and settings.
    get_initial_language() -> str
        Determine the initial language based on system settings or config.
    load_translation_file(language: str, file_path: Path) -> bool
        Load a translation file for the specified language.
    load_translator(language: str) -> None
        Load the translator for the specified language.
    start() -> None
        Start the application with a splash screen and event loop.
    check_language() -> None
        Check if language selection is needed and proceed accordingly.
    show_language_selection() -> None
        Display the language selection screen.
    setup_main_window() -> None
        Set up and display the main application window.
    on_language_selected() -> None
        Handle the selection of a language.
    on_language_cancel() -> None
        Handle cancellation of language selection.
    close_all_windows() -> None
        Close all open windows.
    get_settings(log: Log) -> Optional[QSettings]
        Retrieve or create a QSettings instance.
    get_language_model(log: Log) -> Optional[Language]
        Retrieve or create a Language model instance.
    get_translator(selected_language: str, log: Log)
        -> Tuple[Optional[QTranslator], bool]
        Retrieve or create a translator for the specified language.
    translate_message(translator: Optional[QTranslator], exception: Exception)
        -> str
        Translate an error message using the provided translator.
    """

    def __init__(
        self,
        app: Optional[QApplication] = None,
        settings: Optional[QSettings] = None,
    ) -> None:
        """Initialize the AppLauncher with optional application and settings.

        Parameters
        ----------
        app : Optional[QApplication], optional
            Existing Qt application instance, by default None.
        settings : Optional[QSettings], optional
            Existing settings instance, by default None.

        Returns
        -------
        None

        Notes
        -----
        If no app is provided, a new QApplication is created.
        If no settings are provided, a new QSettings instance is created
        using a config.ini file.
        """
        self.log = Log.get_log()
        self.log.log_info("Starting AppLauncher.")
        self.app = app or QApplication(sys.argv)
        self.translator = QTranslator()
        self.language_model = Language()
        self.splash: Optional[SplashScreen] = None
        self.main_window: Optional[TTeaApp] = None
        self.settings = settings or QSettings(
            PathConfig.inifile("config.ini"), QSettings.IniFormat
        )
        self.language_controller: Optional[LanguageController] = None
        self.current_language = (
            self.get_initial_language()
        )  # Store initial language
        self.load_translator(
            self.current_language
        )  # Load translation for splash screen
        self.has_error = False

    def get_initial_language(self) -> str:
        """Determine the initial language based on system settings or config.

        Returns
        -------
        str
            The language code to use (e.g., 'en_US', 'pt_BR').

        Notes
        -----
        Checks the system language and supported languages. Falls back to
        Language.DEFAULT_LANGUAGE if the system language is not supported.
        If a config file exists, uses the stored language setting if valid.
        """
        system_language = self.language_model.get_system_language().replace(
            "-", "_"
        )
        supported_languages = {
            lang["code"] for lang in self.language_model.get_languages()
        }
        default_language = (
            system_language
            if system_language in supported_languages
            else Language.DEFAULT_LANGUAGE
        )
        config_file = Path(self.settings.fileName())
        if config_file.exists():
            language = self.settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)
            if language in supported_languages:
                return language
        return default_language

    def load_translation_file(self, language: str, file_path: Path) -> bool:
        """Load a translation file for the specified language.

        Parameters
        ----------
        language : str
            The language code (e.g., 'en_US', 'pt_BR').
        file_path : Path
            Path to the translation file.

        Returns
        -------
        bool
            True if the translation file was loaded successfully,
            False otherwise.

        Notes
        -----
        Logs the result of the loading attempt. Installs the translator
        if the file exists and loads successfully.
        """
        if file_path.exists() and self.translator.load(str(file_path)):
            self.app.installTranslator(self.translator)
            self.log.log_info(f"Loaded translation: {language}")
            return True
        self.log.log_warning(f"Translation file not found: {file_path}")
        return False

    def load_translator(self, language: str) -> None:
        """Load the translator for the specified language.

        Parameters
        ----------
        language : str
            The language code to load (e.g., 'en_US', 'pt_BR').

        Returns
        -------
        None

        Notes
        -----
        Attempts to load the translation file for the given language.
        Falls back to the default language if the specified language file
        is not found.
        """
        translation_file = Path(
            PathConfig.translation(language + AppConfig.TRANSLATION_EXTENSION)
        )
        self.log.log_info(f"Trying to load translation: {translation_file}")
        if (
            not self.load_translation_file(language, translation_file)
            and language != Language.DEFAULT_LANGUAGE
        ):
            default_file = Path(
                PathConfig.translation(
                    Language.DEFAULT_LANGUAGE + AppConfig.TRANSLATION_EXTENSION
                )
            )
            self.load_translation_file(Language.DEFAULT_LANGUAGE, default_file)

    def start(self) -> None:
        """Start the application with a splash screen and event loop.

        Returns
        -------
        None

        Notes
        -----
        Displays the splash screen, initiates language checking after a delay,
        and starts the application event loop. Logs the application start and
        exit status.
        """
        self.log.log_info("Application started successfully.")
        self.splash = SplashScreen(self.translator)
        self.splash.show()
        QTimer.singleShot(1000, self.check_language)
        exit_code = self.app.exec()
        self.log.log_info("Application finished successfully.")
        sys.exit(exit_code)

    def check_language(self) -> None:
        """Check if language selection is needed and proceed accordingly.

        Returns
        -------
        None

        Notes
        -----
        If no config file or language setting exists, shows the language
        selection screen. Otherwise, loads the configured language and sets
        up the main window if the language has changed.
        """
        config_file = Path(self.settings.fileName())
        language = self.settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)
        if not config_file.exists() or not language:
            QTimer.singleShot(1000, self.show_language_selection)
        else:
            if (
                language != self.current_language
            ):  # Load only if language changed
                self.load_translator(language)
                self.current_language = language
            self.setup_main_window()

    def show_language_selection(self) -> None:
        """Display the language selection screen.

        Returns
        -------
        None

        Notes
        -----
        Closes the splash screen, shows the language selection view,
        and connects the view's signals to language selection handlers.
        """
        if self.splash and self.splash.isVisible():
            self.splash.close()
            self.splash = None
        self.language_controller = LanguageController(
            self.language_model,
            lambda parent: ViewFactory.get_app_view_factory().create_language_view(
                self.translator, parent
            ),
            parent=None,
        )
        self.language_controller.view.accepted.connect(
            self.on_language_selected
        )
        self.language_controller.view.rejected.connect(self.on_language_cancel)
        self.language_controller.view.show()
        self.log.log_info("Displaying language selection screen")

    def setup_main_window(self) -> None:
        """Set up and display the main application window.

        Returns
        -------
        None

        Notes
        -----
        Creates the main window if not already created, closes the splash
        screen if visible, and shows the main window.
        """
        if not self.main_window:
            self.main_window = TTeaApp(self.translator, self)
            if self.splash and self.splash.isVisible():
                self.splash.finish(self.main_window)
            else:
                self.main_window.show()
            self.log.log_info("Configured main window")

    def on_language_selected(self) -> None:
        """Handle the selection of a language.

        Returns
        -------
        None

        Notes
        -----
        Saves the selected language and date format settings, updates the
        translator if the language has changed, and sets up the main window.
        If no language is selected or the controller is missing, cancels
        the selection process.
        """
        if not self.language_controller:
            self.log.log_warning("No language controller found")
            self.on_language_cancel()
            return
        selected_language = self.language_controller.get_selected_language()
        if selected_language:
            self.settings.setValue(
                AppConfig.SETTINGS_GERAL_LANGUAGE, selected_language
            )
            date_format = (
                AppConfig.DEFAULT_DATE_FORMAT
                if selected_language == Language.DEFAULT_LANGUAGE
                else AppConfig.USA_DATE_FORMAT
            )
            self.settings.setValue(
                AppConfig.SETTINGS_GERAL_DATE_MASK, date_format
            )
            self.settings.sync()
            self.log.log_info(f"Selected language: {selected_language}")
            if (
                selected_language != self.current_language
            ):  # Load only if language changed
                self.load_translator(selected_language)
                self.current_language = selected_language
            self.setup_main_window()
        else:
            self.log.log_warning("No language selected")
            self.on_language_cancel()

    def on_language_cancel(self) -> None:
        """Handle cancellation of language selection.

        Returns
        -------
        None

        Notes
        -----
        Closes all windows, quits the application, and exits with status
        code 0.
        """
        self.log.log_info("Language selection canceled, closing application")
        self.close_all_windows()
        self.app.quit()
        sys.exit(0)

    def close_all_windows(self) -> None:
        """Close all open windows.

        Returns
        -------
        None

        Notes
        -----
        Closes the splash screen and main window if they are visible.
        Sets the splash and main_window attributes to None.
        """
        for window in (
            getattr(self, "splash", None),
            getattr(self, "main_window", None),
        ):
            if window and hasattr(window, "isVisible") and window.isVisible():
                window.close()
        self.splash = self.main_window = None

    def get_settings(self, log: "Log") -> Optional[QSettings]:
        """Retrieve or create a QSettings instance.

        Parameters
        ----------
        log : Log
            Logger instance for logging events.

        Returns
        -------
        Optional[QSettings]
            The QSettings instance, or None if not available.

        Notes
        -----
        Returns the existing settings instance if available, otherwise
        creates a new one using config.ini.
        """
        settings = getattr(self, "settings", None)
        if settings:
            return settings
        settings = QSettings(
            PathConfig.inifile("config.ini"), QSettings.IniFormat
        )
        log.log_info("Created temporary QSettings for translation")
        return settings

    def get_language_model(self, log: "Log") -> Optional[Language]:
        """Retrieve or create a Language model instance.

        Parameters
        ----------
        log : Log
            Logger instance for logging events.

        Returns
        -------
        Optional[Language]
            The Language model instance, or None if not available.

        Notes
        -----
        Returns the existing language model if available, otherwise
        creates a new one.
        """
        language_model = getattr(self, "language_model", None)
        if language_model:
            return language_model
        language_model = Language()
        log.log_info("Created temporary Language model for translation")
        return language_model

    def get_translator(
        self, selected_language: str, log: "Log"
    ) -> Tuple[Optional[QTranslator], bool]:
        """Retrieve or create a translator for the specified language.

        Parameters
        ----------
        selected_language : str
            The language code to load the translator for.
        log : Log
            Logger instance for logging events.

        Returns
        -------
        Tuple[Optional[QTranslator], bool]
            A tuple containing the translator instance (or None) and a boolean
            indicating if a temporary translator was created.

        Notes
        -----
        Returns the existing translator if available, otherwise attempts to
        load a new translator for the specified language.
        """
        translator = getattr(self, "translator", None)
        if translator:
            return translator, False
        temp_translator = QTranslator()
        translation_file = Path(
            PathConfig.translation(
                selected_language + AppConfig.TRANSLATION_EXTENSION
            )
        )
        if translation_file.exists() and temp_translator.load(
            str(translation_file)
        ):
            log.log_info(f"Loaded temporary translation: {selected_language}")
            return temp_translator, True
        log.log_warning(f"Translation file not found: {translation_file}")
        return None, False

    def translate_message(
        self,
        translator: Optional[QTranslator],
        exception: Exception,
    ) -> str:
        """Translate an error message using the provided translator.

        Parameters
        ----------
        translator : Optional[QTranslator]
            Translator for the error message, or None.
        exception : Exception
            The exception to include in the error message.

        Returns
        -------
        str
            The translated or default error message.

        Notes
        -----
        If a translator is provided and translation succeeds, returns the
        translated message. Otherwise, returns the default message.
        """
        default_message = (
            "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
            "Por favor, contate o suporte.\n"
            f"Detalhes do erro: {str(exception)}"
        )
        if not translator:
            return default_message
        translated = translator.translate(
            "AppLauncher",
            "Ocorreu um erro inesperado e a aplicação será encerrada.\n"
            "Por favor, contate o suporte.\n"
            "Detalhes do erro: {0}",
        )
        if translated and not translated.isspace():
            return translated.format(str(exception))
        return default_message


def main() -> None:
    """Entry point for the application.

    Returns
    -------
    None

    Notes
    -----
    Creates and starts an AppLauncher instance.
    """
    launcher = AppLauncher()
    launcher.start()


if __name__ == "__main__":
    main()
