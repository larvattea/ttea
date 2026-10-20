"""Language service: detection, persistence and Qt translators."""

from PySide6.QtCore import QLibraryInfo, QLocale, QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from ttea.app import AppConfig
from ttea.model import AppModel, Language
from ttea.util import PathConfig


class LanguageService:
    """Detect, save and apply the application language.

    Attributes
    ----------
    settings : QSettings
        Configuration file at ``PathConfig.config()``.
    current_language : str
        Language chosen at creation by ``get_initial_language``.

    Notes
    -----
    The application translations are ``.qm`` files in the Qt resources
    (``PathConfig.translation``). Qt's own ``qt_help`` translation is
    also loaded when available, so the help widgets (search, index) are
    translated too.
    """

    def __init__(self):
        self.settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        self._model = Language()
        self.current_language = self.get_initial_language()

    def get_saved_language(self) -> str:
        """Return the saved language, or the default language.

        Returns
        -------
        str
            The code saved under ``AppConfig.SETTINGS_GERAL_LANGUAGE``
            if it is supported, otherwise ``Language.DEFAULT_LANGUAGE``.
        """
        saved = self.settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)
        available = [lang["code"] for lang in self._model.get_languages()]

        if saved and saved in available:
            return saved
        return Language.DEFAULT_LANGUAGE

    def save_language(self, code: str) -> None:
        """Save the user's language choice.

        Parameters
        ----------
        code : str
            Language code, e.g. ``"es_ES"``. It is not validated.

        Notes
        -----
        The configuration file is synced to disk immediately.
        """
        self.settings.setValue(AppConfig.SETTINGS_GERAL_LANGUAGE, code)
        self.settings.sync()

    def get_system_language(self) -> str:
        """Return the language of the operating system.

        Returns
        -------
        str
            ``QLocale.system().name()``, e.g. ``"pt_BR"``.
        """
        return QLocale.system().name()

    def get_initial_language(self) -> str:
        """Return the language to use when the application starts.

        Returns
        -------
        str
            A supported language code.

        Notes
        -----
        Priority:

        1. The saved language, when it differs from the default
           (an explicit user choice).
        2. The system language, if supported: exact match first, then
           the first supported code with the same language prefix (e.g.
           ``en_GB`` gives ``en_US``).
        3. ``Language.DEFAULT_LANGUAGE`` (``pt_BR``).

        A saved ``pt_BR`` cannot be told apart from "nothing saved", so
        it does not override the system language.
        """
        saved = self.get_saved_language()
        if saved != Language.DEFAULT_LANGUAGE:
            return saved

        system_lang = self.get_system_language()  # e.g. "pt_BR", "en_US"

        available_codes = [
            lang["code"] for lang in self._model.get_languages()
        ]

        if system_lang in available_codes:
            return system_lang

        system_prefix = system_lang.split("_")[0].lower()  # "en"
        for code in available_codes:
            if code.lower().startswith(system_prefix):
                return code

        return Language.DEFAULT_LANGUAGE

    def _load_and_install_translator(self, code: str) -> bool:
        """Install the translators of ``code`` in the QApplication.

        Parameters
        ----------
        code : str
            Language code.

        Returns
        -------
        bool
            False if there is no QApplication or the application
            translation cannot be loaded; True otherwise.

        Notes
        -----
        All existing ``QTranslator`` children of the application are
        removed first, even when loading then fails, which leaves the
        texts untranslated (pt_BR source texts). The application
        translator is installed last so it wins over ``qt_help``.
        """
        app = QApplication.instance()
        if not app:
            return False

        for old in app.findChildren(QTranslator):
            app.removeTranslator(old)
            old.deleteLater()

        translator = QTranslator(app)
        path = PathConfig.translation(
            f"{code}{AppConfig.TRANSLATION_EXTENSION}"
        )

        if not translator.load(path):
            return False

        # Qt's own texts of the help widgets (search, index). Optional:
        # without it they stay in English.
        qt_help = QTranslator(app)
        if qt_help.load(
            QLocale(code),
            "qt_help",
            "_",
            QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
        ):
            app.installTranslator(qt_help)

        # Installed last, so the application translations win.
        app.installTranslator(translator)
        return True

    def preview_language(self, code: str) -> bool:
        """Load a language for preview only.

        Parameters
        ----------
        code : str
            Language code.

        Returns
        -------
        bool
            True if the translation was installed.

        Notes
        -----
        Nothing is saved and the date and time masks are not changed.
        """
        return self._load_and_install_translator(code)

    def apply_language(self, code: str) -> bool:
        """Apply a language for good.

        Parameters
        ----------
        code : str
            Language code.

        Returns
        -------
        bool
            True if the translation was installed and the choice saved;
            False if it could not be loaded (nothing is saved).

        Notes
        -----
        Besides installing the translators, this saves the language,
        sets the date and hour/minute masks (US formats for ``en_US``,
        the default formats otherwise) and updates
        ``AppModel.current_language``.
        """
        if not self._load_and_install_translator(code):
            return False

        # Only when applying for good, not in preview
        date_mask = (
            AppConfig.USA_DATE_FORMAT
            if code == "en_US"
            else AppConfig.DEFAULT_DATE_FORMAT
        )

        hour_minute_mask = (
            AppConfig.USA_HOUR_MINUTE_FORMAT
            if code == "en_US"
            else AppConfig.DEFAULT_HOUR_MINUTE_FORMAT
        )

        self.settings.setValue(AppConfig.SETTINGS_GERAL_DATE_MASK, date_mask)
        self.settings.setValue(
            AppConfig.SETTINGS_GERAL_HOUR_MINUTE_MASK, hour_minute_mask
        )

        self.save_language(code)
        model = AppModel.get_instance()
        model.current_language = code
        return True
