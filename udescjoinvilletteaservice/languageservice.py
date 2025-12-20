from typing import Optional

from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from udescjoinvilletteaapp import AppConfig
from udescjoinvilletteautil import PathConfig


class LanguageService:
    """Service: responsável por persistência e aplicação do idioma."""

    def __init__(self):
        self.settings = QSettings(PathConfig.config(), QSettings.IniFormat)

    def get_saved_language(self) -> str:
        """Retorna idioma salvo ou o padrão."""
        from udescjoinvilletteamodel import Language

        saved = self.settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)
        available = [lang["code"] for lang in Language().get_languages()]

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

        # Remove TODOS os tradutores instalados anteriormente
        # (é seguro chamar múltiplas vezes, e evita vazamento de tradutores antigos)
        for translator in app.findChildren(QTranslator):
            app.removeTranslator(translator)

        translator = QTranslator(
            app
        )  # Passa app como parent para evitar GC precoce
        path = PathConfig.translation(f"{code}.qm")

        if translator.load(path):
            app.installTranslator(translator)

            # Lógica extra de máscara de data
            if code == "en_US":
                date_mask = AppConfig.USA_DATE_FORMAT
            else:
                date_mask = AppConfig.DEFAULT_DATE_FORMAT

            self.settings.setValue(
                AppConfig.SETTINGS_GERAL_DATE_MASK, date_mask
            )
            self.save_language(code)
            return True

        return False
