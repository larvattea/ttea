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
        translator = QTranslator()
        path = PathConfig.translation(f"{code}.qm")

        if translator.load(path):
            app = QApplication.instance()
            old = app.property("current_translator")
            if old:
                app.removeTranslator(old)
            app.installTranslator(translator)
            app.setProperty("current_translator", translator)

            # === NEW LOGIC: adjusts date mask according to language ===
            if code == "en_US":
                date_mask = AppConfig.USA_DATE_FORMAT  # "%m/%d/%Y"
            else:
                date_mask = (
                    AppConfig.DEFAULT_DATE_FORMAT
                )  # "%d/%m/%Y" (brazilian standard)

            self.settings.setValue(
                AppConfig.SETTINGS_GERAL_DATE_MASK, date_mask
            )

            self.save_language(code)
            return True
        return False
