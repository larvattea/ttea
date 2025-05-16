import locale
import os
import platform
from typing import List, Dict, Optional

from udescjoinvilletteautil.pathconfig import PathConfig

class Language:
    """Modelo para gerenciar dados de idiomas."""

    LANGUAGES: List[Dict[str, str]] = [
        {
            "code": "pt_BR",
            "description": "Português",
            "flag": PathConfig.image("brazil.png"),
        },
        {
            "code": "en_US",
            "description": "English",
            "flag": PathConfig.image("usa.png"),
        },
    ]

    DEFAULT_LANGUAGE = "pt_BR"  # Idioma padrão em caso de falha

    def __init__(self):
        self.selected_language: Optional[str] = None

    def get_languages(self) -> List[Dict[str, str]]:
        """Retorna a lista de idiomas disponíveis."""
        return self.LANGUAGES

    def set_selected_language(self, language_code: str) -> None:
        """Define o idioma selecionado."""
        self.selected_language = language_code

    def get_selected_language(self) -> Optional[str]:
        """Retorna o idioma selecionado."""
        return self.selected_language

    def get_system_language(self) -> str:
        """Obtém o idioma do sistema operacional no formato 'idioma-país' (ex.: 'pt-BR')."""
        system_locale = locale.getlocale()[0]
        if system_locale:
            return system_locale.replace("_", "-")

        os_name = platform.system()
        if os_name == "Windows":
            import ctypes

            windll = ctypes.windll.kernel32
            locale_id = windll.GetUserDefaultUILanguage()
            return locale.windows_locale.get(locale_id, "en-US")

        if os_name == "Linux":
            for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
                lang = os.getenv(env_var)
                if lang:
                    return lang.split(".")[0].replace("_", "-")

        return "en-US"