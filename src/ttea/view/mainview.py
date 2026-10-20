"""Main window of the T-TEA platform."""

from datetime import date, datetime
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar, QWidget

from ttea.app import AppConfig
from ttea.controller import MainController
from ttea.model import AppModel
from ttea.ui import Ui_MainView
from ttea.util import MessageService
from ttea.window import WindowConfig


class MainView(QMainWindow, Ui_MainView, WindowConfig):
    """Main window: menus, game actions and status bar.

    Parameters
    ----------
    parent : QWidget | None, optional
        Parent widget. Default is None.

    Attributes
    ----------
    controller : MainController
        Controller of the window.
    msg : MessageService
        Service used to show dialogs.
    status_timer : QTimer
        Updates the status bar every second.

    Notes
    -----
    The games are discovered with ``ViewFactory.discover_games()``, and
    each entry of a game's ``menu_actions`` becomes an action in the
    exergames settings submenu (label and icon from the metadata).
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ):
        from ttea.factory import ViewFactory

        super().__init__(parent)
        self.setupUi(self)

        self.setup_window(
            AppConfig.get_title(),
            None,
            WindowConfig.DECREMENT_SIZE_PERCENT,
            5,
            5,
            parent,
        )

        self.controller = MainController(
            self, AppModel.get_instance(), MessageService(self)
        )

        self.act_exit.triggered.connect(self.controller.handle_exit)
        self.act_professional.triggered.connect(
            self.controller.open_professional_list
        )
        self.act_institutionfacility.triggered.connect(
            self.controller.open_institutionfacility_list
        )
        self.act_player.triggered.connect(self.controller.open_player_list)
        # self.act_kartea.triggered.connect(
        #    self.controller.open_kartea_player_config
        # )

        ViewFactory.discover_games()
        for game_name, metadata in ViewFactory._game_metadata.items():
            for action_info in metadata.menu_actions.values():
                act = QAction(action_info["label"], self)
                act.setIcon(QIcon(metadata.icon_path))

                act.triggered.connect(
                    lambda _, g=game_name, m=action_info[
                        "method"
                    ], e=action_info.get(
                        "edit_method"
                    ): self.controller.open_game_action(
                        g, m, edit_method=e
                    )
                )
                self.mnu_settings_exergames_sub.addAction(act)

        self.act_calibration.triggered.connect(
            self.controller.open_calibration
        )

        self.act_calibration_setting.triggered.connect(
            self.controller.open_calibration_setting
        )

        self.act_language.triggered.connect(self.controller.open_language)
        self.act_help.triggered.connect(self.controller.open_help)
        self.act_about.triggered.connect(self.controller.open_about)

        self.act_player_game.triggered.connect(
            self.controller.open_playergamelaunch
        )

        self.msg = MessageService(self)
        self.setup_status_bar()

    def setup_status_bar(self):
        """Show the status bar and start its one-second update timer."""
        self.update_status_info_time()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_info_time)
        self.status_timer.start(1000)

    def update_status_info_time(self):
        """Show the platform version, date and time in the status bar.

        Notes
        -----
        The texts are translated with ``self.tr()`` and the date and
        time use the configured masks. A new ``QStatusBar`` with a new
        label replaces the previous one on every call.
        """
        version = self.tr("Versão da plataforma: {0}")
        version = version.format(AppConfig.VERSION)

        date_mask = AppConfig.get_geral_date_mask()
        hour_mask = AppConfig.get_geral_hour_minute_mask()

        current_date = self.tr("Data atual: {0}").format(
            date.today().strftime(date_mask)
        )
        current_hour = datetime.now().strftime(hour_mask)

        status_text = version + " | " + current_date + " - " + current_hour
        status_bar_label = QLabel(status_text)
        status_bar_label.setAlignment(Qt.AlignRight)
        status_bar_label.setStyleSheet("border: 1px sunken; padding: 2px;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(status_bar_label)
        self.setStatusBar(status_bar)

    def update_status_message(self, message: str, timeout: int = 6000):
        """Show a temporary message in the status bar.

        Parameters
        ----------
        message : str
            Message to show.
        timeout : int, optional
            Time in milliseconds. Default is 6000.
        """
        self.statusBar().showMessage(message, timeout)

    def show_critical_error(self, title: str, text: str):
        """Show a critical error dialog.

        Parameters
        ----------
        title : str
            Dialog title.
        text : str
            Error message.
        """
        self.msg.critical(text, title)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop the status timer and close if the user confirms.

        Parameters
        ----------
        event : QCloseEvent
            Close event; ignored if the user cancels the exit.

        Notes
        -----
        The timer is stopped even when the user cancels, so the clock in
        the status bar stops updating.
        """
        if hasattr(self, "status_timer"):
            self.status_timer.stop()
        if self.controller.try_close():
            event.accept()
        else:
            event.ignore()
