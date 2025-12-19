# udescjoinvilletteacontroller/languagecontroller.py
from typing import Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtGui import QCloseEvent

from udescjoinvilletteamodel import Language
from udescjoinvilletteaservice import LanguageService
from udescjoinvilletteautil import MessageService
from udescjoinvilletteaview import LanguageView


class LanguageController:
    """Controller MVCS completo — idêntico ao PlayerListController."""

    def __init__(
        self,
        model: Language,
        language_view_factory: Callable[[Optional[QObject]], LanguageView],
        parent: Optional[QObject] = None,
    ):
        self.model = model
        self.service = LanguageService()
        self.view = language_view_factory(parent)
        self.msg = MessageService(self.view)

        self._setup_connections()
        self._initialize_view()

    def _setup_connections(self) -> None:
        self.view.btn_confirm.clicked.connect(self.handle_confirm)
        self.view.closeEvent = self.handle_close_event

    def _initialize_view(self) -> None:
        languages = self.model.get_languages()
        self.view.populate_languages(languages)

        # Priority: saved > system > default
        # preferred = (
        #    self.service.get_saved_language()
        #    or self.model.get_system_language().replace("-", "_")
        #    or "pt_BR"
        # )
        # self.view.set_preselected_language(preferred)

    def handle_confirm(self) -> None:
        code = self.view.get_checked_language()
        if not code:
            self.view.show_warning()
            return

        if self.service.apply_language(code):
            self.view.accept()
        else:
            self.msg.critical(self.view.tr("Erro ao carregar o idioma."))

    def handle_close_event(self, event: QCloseEvent) -> None:
        code = self.view.get_checked_language()
        if code and self.service.apply_language(code):
            event.accept()
        else:
            self.view.show_warning()
            event.ignore()
