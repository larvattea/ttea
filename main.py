"""Main module for the T-TEA Qt application entry point."""

import os
import sys

os.environ["QT_LOGGING_RULES"] = "*.debug=false"

from udescjoinvilletteautil import CriticalHooks

CriticalHooks.setup_exception_hooks()

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteafactory import ViewFactory
from udescjoinvillettealog import Log
from udescjoinvilletteaservice import LanguageService
from udescjoinvilletteaview import SplashScreen


class App:
    """Main application class that initializes and runs the Qt app.

    Attributes
    ----------
    app : QApplication | None
        The Qt application instance used for the event loop.
    splash : SplashScreen | None
        The splash screen displayed while the application starts.
    language_view : QDialog | None
        The language selection view instance.
    main_view : QMainWindow | None
        The main application window.
    """

    def __init__(self) -> None:
        """Initialize application state before Qt startup."""
        self.app: QApplication | None = None
        self.splash: SplashScreen | None = None
        self.language_view: QDialog | None = None
        self.main_view: QMainWindow | None = None

    def run(self) -> None:
        """Run the main application and start the Qt event loop.

        This method creates the QApplication, applies the initial language,
        shows the splash screen, optionally prompts the user for language
        selection, and then shows the main window.

        Notes
        -----
        The method handles both first-run language setup and normal startup
        flow. If the language selection dialog is rejected, the application
        exits with status 0.

        Returns
        -------
        None

        Examples
        --------
        >>> app = App()
        >>> app.run()  # doctest: +SKIP
        """
        Log.get_log().log_info("Application started successfully.")

        # Creation of the QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(AppConfig.get_title())
        self.app.setApplicationVersion(AppConfig.VERSION)
        self.app.setWindowIcon(QIcon(AppConfig.ICON_APP))

        # === Detects initial language and applies it ===
        language_service = LanguageService()
        initial_lang = language_service.get_initial_language()
        language_service.preview_language(initial_lang)
        selected_lang = initial_lang

        # ======================
        # SPLASH SCREEN
        # ======================
        self.splash = SplashScreen()
        self.splash.show()
        self.app.processEvents()
        self.splash.raise_()

        if not AppConfig.config_file_exists():
            # === Language selection screen ===
            language_view = (
                ViewFactory.get_app_view_factory().create_language_view()
            )

            # === Applies the initial language as preview ===
            language_view.controller.service.preview_language(initial_lang)
            language_view.retranslateUi(
                language_view
            )  # forces immediate translation

            self.splash.finish(language_view)

            result = language_view.exec()

            if result == QDialog.DialogCode.Rejected:
                sys.exit(0)

            selected_lang = (
                language_view.get_selected_language() or initial_lang
            )

            if selected_lang != initial_lang:
                language_service.apply_language(selected_lang)
        else:
            self.splash.finish(None)

        # === Initializes the app model and menu ===
        self.main_view = ViewFactory.get_app_view_factory().create_main_view()
        self.main_view.show()
        Log.get_log().log_info("Main window shown. Starting event loop.")

        exit_code = self.app.exec()
        Log.get_log().log_info(f"Application exited with code: {exit_code}.")
        sys.exit(exit_code)


if __name__ == "__main__":
    application = App()
    application.run()
