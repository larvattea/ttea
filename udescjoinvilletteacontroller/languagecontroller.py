from typing import Optional
from PySide6.QtCore import Qt
from udescjoinvilletteamodel.language import Language
from udescjoinvilletteaview.languageview import LanguageView


class LanguageController:
    """Controlador para gerenciar a seleção de idioma."""

    def __init__(self, model: Language, view: LanguageView):
        self.model = model
        self.view = view
        self.setup_connections()
        self.initialize_view()

    def setup_connections(self) -> None:
        """Configura as conexões entre a View e o Controller."""
        self.view.confirm_button.clicked.connect(self.handle_confirm)
        self.view.closeEvent = self.handle_close_event

    def initialize_view(self) -> None:
        """Inicializa a View com os dados do Model."""
        languages = self.model.get_languages()
        self.view.populate_languages(languages)

    def handle_confirm(self) -> None:
        """Processa a ação de confirmação do idioma selecionado."""
        selected_language = self.view.get_checked_language()
        if selected_language:
            self.model.set_selected_language(selected_language)
            self.view.accept()
        else:
            self.view.show_warning()

    def handle_close_event(self, event) -> None:
        """Controla o evento de fechamento da janela."""
        selected_language = self.view.get_checked_language()
        if selected_language:
            self.model.set_selected_language(selected_language)
            self.view.accept()
            event.accept()
        else:
            self.view.show_warning()
            event.ignore()

    def get_selected_language(self) -> Optional[str]:
        """Retorna o idioma selecionado."""
        return self.model.get_selected_language()

    def get_system_language(self) -> str:
        """Retorna o idioma do sistema."""
        return self.model.get_system_language()