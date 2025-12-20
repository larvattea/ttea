# udescjoinvilletteacontroller/languagecontroller.py
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTranslator
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication

from udescjoinvilletteamodel import Language
from udescjoinvilletteaservice import LanguageService
from udescjoinvilletteautil import MessageService, PathConfig
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

        # Variável para evitar recarregar o mesmo idioma (evita flicker)
        self._current_preview_lang: Optional[str] = None

        self._setup_connections()
        self._initialize_view()

    def _setup_connections(self) -> None:
        self.view.btn_confirm.clicked.connect(self.handle_confirm)
        self.view.closeEvent = self.handle_close_event
        # Preview imediato ao mudar seleção no ComboBox
        self.view.comboBox.currentIndexChanged.connect(self._preview_language)

    def _initialize_view(self) -> None:
        languages = self.model.get_languages()
        self.view.populate_languages(languages)

        # Prioridade: idioma salvo > idioma do sistema > padrão
        preferred = (
            self.service.get_saved_language()
            or self.model.get_system_language().replace("-", "_")
            or "pt_BR"
        )
        self.view.set_preselected_language(preferred)

        # Define o idioma inicial como o atualmente aplicado no preview
        self._current_preview_lang = preferred

    def _preview_language(
        self,
    ) -> None:  # Removido o parâmetro 'index' não usado
        """Aplica o idioma selecionado como preview (atualiza UI imediatamente)."""
        code = self.view.get_checked_language()
        if not code:
            return

        # Evita recarregar o mesmo idioma (melhora performance e evita flicker)
        if code == self._current_preview_lang:
            return

        app = QApplication.instance()
        if not app:
            return

        # Remove todos os tradutores antigos
        for old in app.findChildren(QTranslator):
            app.removeTranslator(old)

        translator = QTranslator(app)
        path = PathConfig.translation(f"{code}.qm")

        if translator.load(path):
            app.installTranslator(translator)
            self.view.retranslateUi(self.view)  # Força atualização imediata
            self._current_preview_lang = (
                code  # Atualiza o idioma atual do preview
            )
        # Se falhar no load, mantém o anterior (silenciosamente)

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
