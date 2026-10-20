"""Application-wide F1 key handling for the help system.

The F1 shortcut of the main window does not fire while a modal dialog
is open, because Qt blocks window shortcuts of windows shadowed by a
modal dialog. This filter is installed on the QApplication and sees F1
in every window, including modal dialogs.
"""

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt


class HelpKeyFilter(QObject):
    """Call a function whenever F1 is pressed in any window.

    Parameters
    ----------
    callback : Callable[[], None]
        Function called when F1 is pressed. It decides which help topic
        to open.
    parent : QObject or None, optional
        Owner of the filter, usually the QApplication.

    Examples
    --------
    >>> key_filter = HelpKeyFilter(controller.show_help, app)
    >>> app.installEventFilter(key_filter)
    """

    def __init__(
        self, callback: Callable[[], None], parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Intercept F1 key presses and forward them to the callback.

        Parameters
        ----------
        watched : QObject
            Object that received the event.
        event : QEvent
            Event being delivered.

        Returns
        -------
        bool
            True when the event was handled and must not propagate.
        """
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_F1
            and event.modifiers() == Qt.KeyboardModifier.NoModifier
            and not event.isAutoRepeat()
        ):
            self._callback()
            return True
        return super().eventFilter(watched, event)
