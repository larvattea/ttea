from datetime import date
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QMenu, QMenuBar, QStatusBar

# Local module imports
from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteamenu import MenuHandler
from udescjoinvilletteautil import PathConfig
from udescjoinvilletteawindow import WindowConfig


class TTeaApp(QMainWindow, WindowConfig):
    """Main application window for the T-TEA platform.

    This class manages the main window, setting up the menu, status bar, and
    window configurations for the T-TEA platform.

    Attributes
    ----------
    translator : object
        Translator object for internationalization.
    app : object
        Application instance for accessing settings.
    menu_handler : MenuHandler
        Handler for menu actions and interactions.
    settings : QSettings
        Configuration settings loaded from 'config.ini'.
    title : str
        The translated title of the application.

    Methods
    -------
    __init__(translator=None, app=None)
        Initialize the TTeaApp window.
    setup_menu()
        Configure the main menu bar.
    populate_menu(menu, items)
        Populate a menu with items and actions.
    closeEvent(event)
        Handle the window close event.
    setup_status_bar(version)
        Configure the status bar with version and date information.
    get_title()
        Get the translated title of the application.
    """

    def __init__(
        self, translator: Optional[object] = None, app: Optional[object] = None
    ) -> None:
        """Initialize the TTeaApp window.

        Configures the main window, menu, and status bar using the provided
        translator and application instance.

        Parameters
        ----------
        translator : object, optional
            Translator object for internationalization (default is None).
        app : object, optional
            Application instance for accessing settings (default is None).

        Returns
        -------
        None

        Notes
        -----
        - Inherits from QMainWindow and WindowConfig for GUI and window setup.
        - Initializes the menu handler and settings from 'config.ini'.
        - Calls setup_window, setup_menu, and setup_status_bar
        for initialization.
        """
        super().__init__()
        self.translator = translator  # Translator object from main.py
        self.app = app
        self.menu_handler = MenuHandler(self)
        self.settings = QSettings(
            PathConfig.inifile("config.ini"), QSettings.IniFormat
        )
        self.title = AppConfig.get_title()  # Set title attribute
        self.setup_window(self.title, AppConfig.ICON_APP)
        self.setup_menu()
        self.setup_status_bar(AppConfig.VERSION)

    def setup_menu(self) -> None:
        """Configure the main menu bar.

        Creates and populates the menu bar with menus for registration,
        exergames, configurations, and help, based on available game paths.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves game paths from PathConfig.path_games().
        - Assigns icons to game menu items using a predefined mapping.
        - Dynamically populates menus with actions and separators.
        - Menus include Cadastro, Exergames, Configurações, and Ajuda.
        """

        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        paths = PathConfig.path_games()
        games = []
        helps = []

        for path in paths:
            path = (
                path.replace(
                    AppConfig.PLATAFORM_SUFIX.lower(),
                    AppConfig.PLATAFORM_SUFIX,
                )
                if AppConfig.PLATAFORM_SUFIX.lower() in path
                else path
            )
            if path:
                path = path[0].upper() + path[1:]
            # Icon mapping per game
            game_icons = {
                "kartea": PathConfig.icon("kartea4.ico")
                # Add other games here
            }
            # Use specific or generic icon as fallback
            icon_path = game_icons.get(
                path.lower(), PathConfig.image("kartea.png")
            )
            games.append((path, self.menu_handler.do_nothing, icon_path))
            helps.append(
                (
                    AppConfig.PLATAFORM_MANUAL + " " + path,
                    self.menu_handler.menu_help,
                )
            )

        menu_configs = [
            (
                self.tr("&Cadastro"),
                [
                    (self.tr("&Jogador"), self.menu_handler.menu_player),
                    (self.tr("&Sair"), self.menu_handler.menu_exit),
                ],
            ),
            (self.tr("&Exergames"), games),
            (
                self.tr("C&onfigurações"),
                games
                + [(self.tr("&Calibração"), self.menu_handler.do_nothing)],
            ),
            (
                self.tr("&Ajuda"),
                helps + [(self.tr("&Sobre..."), self.menu_handler.menu_about)],
            ),
        ]

        for menu_name, items in menu_configs:
            menu = QMenu(menu_name, self)
            self.populate_menu(menu, items)
            menubar.addMenu(menu)

    def populate_menu(
        self, menu: QMenu, items: List[Tuple[str, Callable, Optional[str]]]
    ) -> None:
        """Populate a menu with items and actions.

        Adds menu items with associated actions and optional icons, including
        separators for specific items.

        Parameters
        ----------
        menu : QMenu
            The menu to populate with items.
        items : list of tuples
            List of tuples containing (label, action) or
            (label, action, icon_path) for menu items.

        Returns
        -------
        None

        Notes
        -----
        - Adds separators before 'Sair', 'Calibração', and 'Sobre...' items.
        - Assigns icons to menu items if an icon path is provided in the tuple.
        """

        for item in items:
            label, action = item[0], item[1]
            # Check if separator should be added
            if label in [
                self.tr("&Sair"),
                self.tr("&Calibração"),
                self.tr("&Sobre..."),
            ]:
                menu.addSeparator()
            # Create the menu action
            menu_action = menu.addAction(label, action)
            # Add icon if any (for game items)
            if (
                len(item) > 2 and item[2]
            ):  # Checks if there is a third element (icon_path)
                menu_action.setIcon(QIcon(item[2]))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the window close event.

        Overrides the default close event to trigger the confirm_exit action.

        Parameters
        ----------
        event : QCloseEvent
            The close event triggered by the window.

        Returns
        -------
        None

        Notes
        -----
        Delegates the handling of the close event to the menu_handler's
        confirm_exit method to ensure proper exit confirmation.
        """
        self.menu_handler.menu_exit(event)

    def setup_status_bar(self, version: str) -> None:
        """Configure the status bar.

        Displays version information and the current date in the status bar.

        Parameters
        ----------
        version : str
            The version number to display in the status bar.

        Returns
        -------
        None

        Notes
        -----
        - Retrieves date format from settings (SETTINGS_GERAL_DATE_MASK).
        - Aligns status bar text to the right with a styled border.
        - Displays the platform version and current date.
        """

        mask = self.settings.value(AppConfig.SETTINGS_GERAL_DATE_MASK, None)
        status_text = ("{} {} - {} {}").format(
            self.tr("Versão da Plataforma:"),
            version,
            self.tr("Data Atual:"),
            date.today().strftime(mask),
        )
        status_bar_label = QLabel(status_text)
        status_bar_label.setAlignment(Qt.AlignRight)
        status_bar_label.setStyleSheet("border: 1px sunken; padding: 2px;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(status_bar_label)
        self.setStatusBar(status_bar)

    def get_title(self) -> str:
        """Get the translated title of the application.

        Returns
        -------
        str
            The translated title of the T-TEA platform.

        Notes
        -----
        Uses QCoreApplication.translate in AppConfig to ensure the title
        is translated according to the current language settings.
        """
        return self.title
