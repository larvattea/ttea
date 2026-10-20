"""Main entry point of the T-TEA Qt application.

This module sets the Qt logging rules (debug messages off) when it is
imported and defines the ``App`` class, which starts the application and
its Qt event loop, and the ``main`` function used by the ``dev`` script
of ``pyproject.toml``.
"""

import os
import sys

os.environ["QT_LOGGING_RULES"] = "*.debug=false"

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

from ttea.app import AppConfig
from ttea.controller import HelpController
from ttea.factory import ViewFactory
from ttea.log import Log
from ttea.service import LanguageService
from ttea.util import CriticalHooks, HelpKeyFilter
from ttea.view import SplashScreen


class App:
    """Main application class that initializes and runs the Qt app.

    Attributes
    ----------
    app : QApplication | None
        The Qt application instance used for the event loop.
    splash : SplashScreen | None
        The splash screen displayed while the application starts.
    language_view : QDialog | None
        The language selection view instance (not set by ``run``, which
        uses a local variable).
    main_view : QMainWindow | None
        The main application window.
    help_key_filter : HelpKeyFilter | None
        Application-wide F1 handler, active in every window.

    Methods
    -------
    run()
        Create the Qt application, initialize the language, show the
        splash screen and the main window, and run the event loop.
    """

    def __init__(self) -> None:
        self.app: QApplication | None = None
        self.splash: SplashScreen | None = None
        self.language_view: QDialog | None = None
        self.main_view: QMainWindow | None = None
        self.help_key_filter: HelpKeyFilter | None = None

    def run(self) -> None:
        """Start the application and run the Qt event loop.

        Notes
        -----
        Steps:

        1. Install the global exception hooks and log the start.
        2. Register the ``qthelp`` URL scheme (before the QApplication).
        3. Create the QApplication (name, version, icon) and install the
           F1 help filter.
        4. Detect the initial language (``get_initial_language``) and
           install it as a preview.
        5. Show the splash screen. On the first run (no configuration
           file), the language dialog is shown; rejecting it exits with
           status 0, and a different choice is applied and saved.
        6. Show the main window and run the event loop.

        This method does not return: it ends with ``sys.exit`` and the
        exit code of the event loop, which is logged.
        """
        CriticalHooks.setup_exception_hooks()
        Log.get_log().log_info("Application started successfully.")

        # Qt WebEngine (help window) must be set up before the
        # QApplication exists.
        self._register_help_scheme()

        # Creation of the QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(AppConfig.get_title())
        self.app.setApplicationVersion(AppConfig.VERSION)
        self.app.setWindowIcon(QIcon(AppConfig.ICON_APP))

        # F1 opens the help of the active screen, also in modal dialogs
        self.help_key_filter = HelpKeyFilter(
            HelpController.instance().show_help, self.app
        )
        self.app.installEventFilter(self.help_key_filter)

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

    @staticmethod
    def _register_help_scheme() -> None:
        """Register the ``qthelp`` URL scheme of the help window."""
        # Imported here so the help module is the only one that loads
        # Qt WebEngine; importing App (e.g. in tests) stays light.
        from ttea.util import helpschemehandler  # noqa: PLC0415

        helpschemehandler.HelpSchemeHandler.register_scheme()


def main() -> None:
    """Start the T-TEA application."""
    application = App()
    application.run()


if __name__ == "__main__":
    main()
