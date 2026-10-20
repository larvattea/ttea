"""Global application state shared by the controllers."""

from PySide6.QtCore import QSettings

from ttea.app import AppConfig
from ttea.util import PathConfig


class AppModel:
    """Global state of the application session (singleton).

    Attributes
    ----------
    language_model : Language
        Supported languages; used by ``LanguageController``.
    _instance : AppModel | None, class attribute
        The single instance.
    _initialized : bool, class attribute
        Whether the instance was already initialized.

    Notes
    -----
    ``AppModel()`` always returns the same object, and its state is
    set up only on the first call. At that time the language saved
    in the configuration file (``PathConfig.config()``, key
    ``AppConfig.SETTINGS_GERAL_LANGUAGE``, read with ``QSettings``)
    becomes the current language if it is supported; otherwise
    ``Language.DEFAULT_LANGUAGE`` is used.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Return the single instance, creating it on the first call.

        Returns
        -------
        AppModel
            The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if AppModel._initialized:
            return

        from ttea.model import Language

        self.language_model = Language()  # only LanguageController

        settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        saved_lang = settings.value(AppConfig.SETTINGS_GERAL_LANGUAGE)

        available_codes = [
            lang["code"] for lang in self.language_model.get_languages()
        ]

        if saved_lang and saved_lang in available_codes:
            self._current_language: str = saved_lang
        else:
            self._current_language: str = Language.DEFAULT_LANGUAGE

        AppModel._initialized = True

    # ------------------------------------------------------------------
    # Current language (validated on assignment)
    # ------------------------------------------------------------------
    @property
    def current_language(self) -> str:
        """Code of the language currently in use, e.g. ``"pt_BR"``.

        Notes
        -----
        Setting an unsupported code selects
        ``Language.DEFAULT_LANGUAGE`` instead. The setter does not save
        the language to the configuration file.
        """
        return self._current_language

    @current_language.setter
    def current_language(self, value: str) -> None:
        from ttea.model import Language

        available_codes = [
            lang["code"] for lang in self.language_model.get_languages()
        ]
        if value in available_codes:
            self._current_language = value
        else:
            self._current_language = Language.DEFAULT_LANGUAGE

    # ------------------------------------------------------------------
    # Optional helper
    # ------------------------------------------------------------------
    def is_english(self) -> bool:
        """Check whether the current language is English.

        Returns
        -------
        bool
            True if ``current_language`` is ``"en_US"``.
        """
        return self.current_language == "en_US"

    @classmethod
    def get_instance(cls) -> "AppModel":
        """Return the single instance of the class.

        Returns
        -------
        AppModel
            The singleton instance, created if needed.
        """
        if cls._instance is None:
            cls._instance = cls()  # runs __new__ and __init__
        return cls._instance
