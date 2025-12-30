from typing import Dict, List

# Local module import
from udescjoinvilletteautil import PathConfig


class Language:
    """Model for managing language data.

    Responsável apenas pelos dados estáticos dos idiomas suportados
    e pelo idioma selecionado pelo usuário (em memória).

    Attributes
    ----------
    LANGUAGES : List[Dict[str, str]]
        Lista de idiomas disponíveis na aplicação.
    DEFAULT_LANGUAGE : str
        Idioma padrão em caso de falha.
    """

    LANGUAGES = [
        {
            "code": "pt_BR",
            "description": "Português",
            "flag": PathConfig.flag("brazil"),
        },
        {
            "code": "es_ES",
            "description": "Español",
            "flag": PathConfig.flag("spain"),
        },
        {
            "code": "en_US",
            "description": "English",
            "flag": PathConfig.flag("usa"),
        },
    ]

    DEFAULT_LANGUAGE = "pt_BR"

    def __init__(self) -> None:
        self.selected_language: str | None = None

    def get_languages(self) -> List[Dict[str, str]]:
        """Retorna a lista de idiomas disponíveis."""
        return self.LANGUAGES

    def set_selected_language(self, language_code: str) -> None:
        """Define o idioma selecionado pelo usuário (em memória)."""
        self.selected_language = language_code

    def get_selected_language(self) -> str | None:
        """Retorna o idioma selecionado pelo usuário."""
        return self.selected_language
