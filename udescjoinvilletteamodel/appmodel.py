# udescjoinvillettea/mvcs/model/appmodel.py
from typing import Optional

from PySide6.QtCore import QSettings

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteautil import PathConfig


class AppModel:
    """Estado global da aplicação (sessão ativa)."""

    def __init__(self):
        from udescjoinvilletteamodel import Language

        self.language_model = Language()  # usado apenas no LanguageController
        self.current_player_id: Optional[int] = None

        # === Carrega o idioma atual salvo nas configurações ===
        settings = QSettings(
            PathConfig.config("config.ini"), QSettings.IniFormat
        )
        saved_lang = settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)

        # Valida se o idioma salvo é um dos suportados
        available_codes = [
            lang["code"] for lang in self.language_model.get_languages()
        ]

        if saved_lang and saved_lang in available_codes:
            self._current_language: str = saved_lang
        else:
            self._current_language: str = Language.DEFAULT_LANGUAGE

    # ------------------------------------------------------------------
    # Property para acesso seguro ao idioma atual
    # ------------------------------------------------------------------
    @property
    def current_language(self) -> str:
        """Retorna o código do idioma atualmente em uso."""
        return self._current_language

    @current_language.setter
    def current_language(self, value: str) -> None:
        """Define o idioma atual, garantindo que seja válido."""
        from udescjoinvilletteamodel import Language

        available_codes = [
            lang["code"] for lang in self.language_model.get_languages()
        ]
        if value in available_codes:
            self._current_language = value
        else:
            # Fallback seguro para o idioma padrão
            self._current_language = Language.DEFAULT_LANGUAGE

    # ------------------------------------------------------------------
    # Método auxiliar opcional (útil se precisar em outros lugares)
    # ------------------------------------------------------------------
    def is_english(self) -> bool:
        """Conveniência para verificar se o idioma atual é inglês."""
        return self.current_language == "en_US"
