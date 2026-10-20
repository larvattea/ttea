"""Controller of the language selection window."""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject

from ttea.model import Language
from ttea.service import LanguageService
from ttea.util import MessageService

if TYPE_CHECKING:
    from ttea.view import LanguageView


class LanguageController(QObject):
    """Controller of the language selection window.

    Parameters
    ----------
    view : LanguageView
        The language dialog.
    service : LanguageService | None, optional
        Language service. Default is None, which creates a new
        ``LanguageService``.

    Attributes
    ----------
    view : LanguageView
        The language dialog.
    service : LanguageService
        Language service.
    model : Language
        Supported languages: the ``language_model`` of the parent's
        ``AppModel`` when available, otherwise a new ``Language``.

    Notes
    -----
    Selecting a language previews it (the dialog is retranslated);
    confirming or closing the dialog applies and saves it.
    """

    def __init__(
        self, view: "LanguageView", service: Optional[LanguageService] = None
    ):
        self.view = view
        self.service = service or LanguageService()

        self.model = (
            p.model.language_model
            if (p := view.parent()) and hasattr(p, "model") and p.model
            else Language()
        )

        self._current_preview_lang = None
        self._initialize_view()

    def _initialize_view(self):
        """List the languages and preselect the initial language."""
        self.view.populate_languages(self.model.get_languages())
        preferred = self.service.get_initial_language()
        self.view.set_preselected_language(preferred)
        self._current_preview_lang = preferred

    def handle_preview(self):
        """Preview the selected language in the dialog.

        Notes
        -----
        Does nothing if no language is selected or it is already
        previewed. The translators are installed without saving, and the
        dialog is retranslated.
        """
        code = self.view.get_selected_language()
        if not code or code == self._current_preview_lang:
            return
        if self.service.preview_language(code):
            self.view.retranslateUi(self.view)
            self._current_preview_lang = code

    def handle_confirm(self):
        """Apply the selected language and close the dialog.

        Notes
        -----
        Without a selection, a warning is shown. If the language cannot
        be applied, an error message (translated with ``self.tr()``) is
        shown and the dialog stays open.
        """
        code = self.view.get_selected_language()
        if not code:
            self.view.show_warning()
            return
        if self.service.apply_language(code):
            self.view.accept()
        else:
            MessageService(self.view).critical(
                self.tr("Erro ao carregar o idioma.")
            )

    def handle_close_event(self, event):
        """Apply the selected language when the dialog is closed.

        Parameters
        ----------
        event : QCloseEvent
            Close event of the view; it is ignored (the dialog stays
            open) when no language is selected or it cannot be applied.
        """
        code = self.view.get_selected_language()
        if code and self.service.apply_language(code):
            event.accept()
        else:
            self.view.show_warning()
            event.ignore()
