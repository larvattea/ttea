from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject

from udescjoinvilletteamodel import Language
from udescjoinvilletteaservice import LanguageService
from udescjoinvilletteautil import MessageService

if TYPE_CHECKING:
    from udescjoinvilletteaview import LanguageView


class LanguageController(QObject):
    def __init__(
        self, view: "LanguageView", service: Optional[LanguageService] = None
    ):
        self.view = view
        self.service = service or LanguageService()
        self.model = (
            view.parent().model.language_model if view.parent() else Language()
        )  # ou injetar

        self._current_preview_lang = None
        self._initialize_view()

    def _initialize_view(self):
        self.view.populate_languages(self.model.get_languages())
        preferred = self.service.get_initial_language()
        self.view.set_preselected_language(preferred)
        self._current_preview_lang = preferred
        # Preview inicial já aplicado via serviço ou main

    def handle_preview(self):
        code = self.view.get_selected_language()
        if not code or code == self._current_preview_lang:
            return
        if self.service.preview_language(code):
            self.view.retranslateUi(self.view)
            self._current_preview_lang = code

    def handle_confirm(self):
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
        code = self.view.get_selected_language()
        if code and self.service.apply_language(code):
            event.accept()
        else:
            self.view.show_warning()
            event.ignore()
