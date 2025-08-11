from typing import Optional

from PySide6.QtCore import (QEasingCurve, QPropertyAnimation, Qt, QTimer,
                            QTranslator)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QSplashScreen

# Local module import
from udescjoinvilletteautil import PathConfig


class SplashScreen(QSplashScreen):
    """A custom splash screen with a progress bar and status messages.

    This class extends QSplashScreen to display a loading screen with a logo,
    a progress bar, and dynamic status messages that update based on progress.
    It includes animations and supports translation for status messages.

    Parameters
    ----------
    translator : QTranslator, optional
        The translator object for handling internationalization
        (default is None).

    Attributes
    ----------
    translator : QTranslator
        The translator object used for status message localization.
    status_label : QLabel
        Label displaying the current status message.
    progress_bar : QProgressBar
        Progress bar showing loading progress.
    animation : QPropertyAnimation
        Animation for the progress bar value.
    progress : int
        Current progress value (0 to 100).
    timer : QTimer
        Timer to trigger progress updates.
    main_window : QWidget
        Reference to the main application window.

    Methods
    -------
    update_layout()
        Adjust the layout of the progress bar and status label.
    update_translation()
        Update the status label text based on the current translation.
    update_progress()
        Update the progress bar and status label based on progress.
    finish_loading()
        Display the main window and close the splash screen.
    finish(main_window)
        Associate the main window with the splash screen.
    show()
        Display the splash screen only if it is not already visible.
    """

    def __init__(self, translator: Optional["QTranslator"] = None) -> None:
        """Initialize the splash screen with a logo, progress bar,
        and status label.

        Parameters
        ----------
        translator : QTranslator, optional
            The translator object for handling internationalization
            (default is None).

        Returns
        -------
        None

        Notes
        -----
        - Loads the logo from `PathConfig.image("ttealogo.png")`.
        - Sets window flags for always-on-top and translucent background.
        - Initializes the progress bar and status label with custom styles.
        - Starts a timer to update progress and an animation for smooth
        progress bar transitions.
        """
        pixmap = QPixmap(PathConfig.image("ttealogo.png"))
        super().__init__(pixmap)

        self.translator = translator  # Translate object from main.py
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.status_label = QLabel(self.tr("Iniciando..."), self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: white;
            font-size: 14px;
            font-weight: bold;
            background: rgba(0, 0, 0, 150);
            padding: 5px;
        """
        )

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #ffffff;
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 200);
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc00, stop:1 #006600);
                border-radius: 3px;
            }
        """
        )

        self.update_layout()

        self.animation = QPropertyAnimation(self.progress_bar, b"value")
        self.animation.setDuration(3000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(750)

        self.animation.start()
        self.main_window = None

    def update_layout(self) -> None:
        """Adjust the layout of the progress bar and status label.

        This method positions the progress bar and status label relative to the
        splash screen's pixmap dimensions, ensuring they are centered and
        appropriately spaced.

        Returns
        -------
        None

        Notes
        -----
        - The progress bar is set to 60% of the pixmap width and positioned
        near the bottom.
        - The status label spans the full width and is placed above the
        progress bar.
        """
        pixmap = self.pixmap()
        width = pixmap.width()
        height = pixmap.height()

        bar_width = width * 0.6
        self.progress_bar.setGeometry(
            int((width - bar_width) / 2), height - 60, int(bar_width), 20
        )

        self.status_label.setGeometry(0, height - 90, width, 30)

    def update_translation(self) -> None:
        """Update the status label text based on the current translation.

        This method updates the status label with translated messages
        corresponding to the current progress value.

        Returns
        -------
        None

        Notes
        -----
        - Uses a dictionary to map progress milestones (0, 25, 50, 75, 100)
        to translated messages.
        - Updates the label with the message corresponding to the nearest
        progress milestone.
        """
        status_messages = {
            0: self.tr("Iniciando..."),
            25: self.tr("Carregando módulos..."),
            50: self.tr("Inicializando interface..."),
            75: self.tr("Verificando conexões..."),
            100: self.tr("Pronto!"),
        }
        # Atualiza o texto atual baseado no progresso
        for progress, message in status_messages.items():
            if self.progress <= progress:
                self.status_label.setText(message)
                break

    def update_progress(self) -> None:
        """Update the progress bar and status label based on progress.

        Increments the progress by 25 and updates the status label
        with the corresponding
        translated message. Stops the timer and triggers `finish_loading`
        when progress reaches 100.

        Returns
        -------
        None

        Notes
        -----
        - Progress increments in steps of 25 (0, 25, 50, 75, 100).
        - The timer stops when progress reaches 100, and a delayed call
        to `finish_loading` is scheduled.
        """
        self.progress += 25
        status_messages = {
            25: self.tr("Carregando módulos..."),
            50: self.tr("Inicializando interface..."),
            75: self.tr("Verificando conexões..."),
            100: self.tr("Pronto!"),
        }

        if self.progress in status_messages:
            self.status_label.setText(status_messages[self.progress])

        if self.progress >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self.finish_loading)

    def finish_loading(self) -> None:
        """Display the main window and close the splash screen.

        Shows the main application window if it exists and is not
        already visible, then closes the splash screen.

        Returns
        -------
        None

        Notes
        -----
        - Ensures the main window is only shown if it is not already visible.
        """
        if self.main_window and not self.main_window.isVisible():
            self.main_window.show()
        self.close()

    def finish(self, main_window) -> None:
        """Associate the main window with the splash screen.

        Sets the main window reference and triggers `finish_loading`
        if progress is complete.

        Parameters
        ----------
        main_window : QWidget
            The main application window to be shown when loading is complete.

        Returns
        -------
        None

        Notes
        -----
        - Does not immediately show the main window; it waits for
        progress to reach 100.
        """
        self.main_window = main_window
        if self.progress >= 100:
            self.finish_loading()

    def show(self) -> None:
        """Display the splash screen only if it is not already visible.

        Overrides the parent `show` method to prevent multiple displays
        of the splash screen.

        Returns
        -------
        None

        Notes
        -----
        - Ensures the splash screen is shown only once by checking visibility.
        """
        if not self.isVisible():
            super().show()
