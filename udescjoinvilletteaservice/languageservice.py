from PySide6.QtCore import QLocale, QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteamodel import Language  # ajuste o caminho se necessário
from udescjoinvilletteautil import PathConfig


class LanguageService:
    """Service: responsável por persistência, aplicação e detecção do idioma."""

    def __init__(self):
        self.settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        self._model = (
            Language()
        )  # Instância do model para acessar dados estáticos
        self.current_language = self.get_initial_language()

    def get_saved_language(self) -> str:
        """Retorna idioma salvo ou o padrão."""
        saved = self.settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)
        available = [lang["code"] for lang in self._model.get_languages()]

        if saved and saved in available:
            return saved
        return Language.DEFAULT_LANGUAGE

    def save_language(self, code: str) -> None:
        """Salva escolha do usuário."""
        self.settings.setValue(AppConfig.SETTINGS_GERAL_LANGUAGE, code)
        self.settings.sync()

    def apply_language(self, code: str) -> bool:
        """Carrega .qm e instala no QApplication."""
        app = QApplication.instance()
        if not app:
            return False

        # Remove todos os tradutores instalados anteriormente
        for translator in app.findChildren(QTranslator):
            app.removeTranslator(translator)
            translator.deleteLater()

        translator = QTranslator(app)  # app como parent para evitar GC precoce
        path = PathConfig.translation(
            f"{code}{AppConfig.TRANSLATION_EXTENSION}"
        )

        if translator.load(path):
            app.installTranslator(translator)

            # Lógica extra de máscara de data
            date_mask = (
                AppConfig.USA_DATE_FORMAT
                if code == "en_US"
                else AppConfig.DEFAULT_DATE_FORMAT
            )

            self.settings.setValue(
                AppConfig.SETTINGS_GERAL_DATE_MASK, date_mask
            )
            self.save_language(code)
            return True

        return False

    def get_system_language(self) -> str:
        """Detecta o idioma do sistema usando QLocale (mais confiável no Qt)."""
        # Retorna algo como "en_US", "pt_BR", etc.
        return QLocale.system().name()

    def get_initial_language(self) -> str:
        """Retorna o idioma que deve ser usado na inicialização da aplicação.

        Prioridade:
        1. Idioma salvo nas configurações (se for diferente do padrão -> escolha explícita do usuário)
        2. Idioma do sistema operacional, se suportado pela aplicação
        3. Idioma padrão da aplicação (pt_BR)
        """
        # 1. Idioma salvo previamente pelo usuário
        saved = self.get_saved_language()
        if saved != Language.DEFAULT_LANGUAGE:  # Indica escolha intencional
            return saved

        # 2. Detecta idioma do sistema
        system_lang = self.get_system_language()  # ex: "pt-BR", "en-US"

        # Lista de códigos suportados no formato Qt (pt_BR, en_US, es_ES)
        available_codes = [
            lang["code"] for lang in self._model.get_languages()
        ]

        # Match exato (ex: "en_US" está na lista?)
        if system_lang in available_codes:
            return system_lang

        # Fallback por prefixo (ex: o sistema é "en_GB", mas só temos "en_US")
        system_prefix = system_lang.split("_")[0].lower()  # "en"
        for code in available_codes:
            if code.startswith(system_prefix):
                return code

        # 3. Fallback final
        return Language.DEFAULT_LANGUAGE
