"""Controller that opens the help window on the right topic.

It is shared by the Help menu and the application-wide F1 key. It keeps
a single help window, recreates it when the language changes and makes
it usable while a modal dialog is open.
"""

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QApplication, QDialog, QWidget

from ttea.log import Log
from ttea.model import AppModel
from ttea.service.helpservice import HelpService, HelpUnavailableError
from ttea.util import MessageService


class HelpController(QObject):
    """Open and manage the help window.

    Parameters
    ----------
    service : HelpService | None, optional
        Help service; a new one is created when omitted.
    parent : QObject | None, optional
        Owner of the controller, usually the QApplication.

    Attributes
    ----------
    service : HelpService
        Help service.
    _instance : HelpController | None, class attribute
        Controller shared by the application.

    Methods
    -------
    instance()
        Return the shared controller.
    show_help(topic=None)
        Show the help at ``topic`` or at the topic of the active screen.

    Notes
    -----
    Typical use: ``HelpController.instance().show_help()`` for the
    active screen, or ``show_help("calibracao")`` for a topic. The
    error message shown when the help is missing is translated with
    ``self.tr()``.
    """

    _instance: "HelpController | None" = None
    _WATCHED_PROPERTY = "_help_owner_watched"

    def __init__(
        self,
        service: HelpService | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.service = service or HelpService()
        self._view = None  # HelpView, created on first use
        self._wanted_visible = False

    @classmethod
    def instance(cls) -> "HelpController":
        """Return the controller shared by the whole application."""
        if cls._instance is None:
            cls._instance = cls(parent=QApplication.instance())
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_help(self, topic: str | None = None) -> None:
        """Show the help window.

        Parameters
        ----------
        topic : str | None, optional
            Topic id from ``HelpService.TOPICS``. When omitted, the
            topic comes from the widget with focus (F1 behaviour).
        """
        origin = QApplication.focusWidget() or QApplication.activeWindow()
        if self._is_help_window(origin):
            return  # F1 pressed inside the help itself

        if topic is None:
            topic = self.service.topic_for_widget(origin)

        try:
            view = self._get_view()
        except HelpUnavailableError as error:
            Log.get_log().log_warning(f"Help unavailable: {error}")
            MessageService.critical_global(
                self.tr(
                    "Não foi possível abrir a ajuda. Verifique se os "
                    "arquivos de ajuda estão instalados."
                )
            )
            return

        self._attach_to_active_modal(view)
        view.show_url(self.service.topic_url(view.engine, topic))
        self._wanted_visible = True
        view.show()
        view.raise_()
        view.activateWindow()

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------
    def _get_view(self):
        """Return the help window, new if the language changed."""
        language = self.service.help_language(
            AppModel.get_instance().current_language
        )
        if self._view is not None and self._view.language != language:
            self._view.close()
            self._view.deleteLater()
            self._view = None

        if self._view is None:
            # Imported here so Qt WebEngine is loaded only when the help
            # is opened for the first time.
            from ttea.view.helpview import HelpView  # noqa: PLC0415

            engine = self.service.create_engine(language)
            home = self.service.topic_url(engine, HelpService.HOME_TOPIC)
            self._view = HelpView(engine, language, home)
            self._view.closed.connect(self._on_view_closed)
        return self._view

    def _is_help_window(self, widget: QWidget | None) -> bool:
        """Return True if ``widget`` belongs to the help window."""
        return (
            self._view is not None
            and widget is not None
            and widget.window() is self._view
        )

    def _attach_to_active_modal(self, view: QWidget) -> None:
        """Make the help a child window of the open modal dialog.

        Qt blocks every window outside an open modal dialog. As a child
        window of the dialog, the help keeps receiving mouse and
        keyboard input.
        """
        modal = QApplication.activeModalWidget()
        owner = modal if modal is not view else None
        self._set_owner(view, owner)
        self._watch(owner)

    @Slot(int)
    def _on_owner_finished(self, _result: int) -> None:
        """Move the help out of a dialog that is closing.

        Without this, the help would be destroyed with the dialog. It
        moves to the next open modal dialog, or becomes a top-level
        window again.
        """
        if self._view is None:
            return
        closing = self.sender()
        modal = QApplication.activeModalWidget()
        owner = modal if modal is not closing else None
        self._set_owner(self._view, owner)
        self._watch(owner)
        if self._wanted_visible:
            self._view.show()

    def _watch(self, owner: QWidget | None) -> None:
        """Be notified once when the owner dialog closes."""
        if isinstance(owner, QDialog) and not owner.property(
            self._WATCHED_PROPERTY
        ):
            owner.setProperty(self._WATCHED_PROPERTY, True)
            owner.finished.connect(self._on_owner_finished)

    @staticmethod
    def _set_owner(view: QWidget, owner: QWidget | None) -> None:
        """Change the parent of ``view``, keeping it a window."""
        if view.parentWidget() is owner:
            return
        geometry = view.geometry()
        visible = view.isVisible()
        view.setParent(owner, Qt.WindowType.Window)
        view.setGeometry(geometry)
        if visible:
            view.show()

    @Slot()
    def _on_view_closed(self) -> None:
        """Remember that the user closed the help."""
        self._wanted_visible = False
