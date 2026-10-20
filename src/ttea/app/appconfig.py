"""Application configuration constants and helper methods.

This module centralizes application path constants, version information,
format settings, and helper methods for translated titles and config
file checks.
"""

from PySide6.QtCore import QCoreApplication, QSettings

from ttea.util import PathConfig


class AppConfig:
    """Hold application configuration constants and helper methods.

    Attributes
    ----------
    ICON_APP : str, class attribute
        Qt resource path of the application icon.
    LOGO_APP : str, class attribute
        Qt resource path of the application logo.
    PLATAFORM_SUFFIX : str, class attribute
        Suffix identifier of the platform (``"TEA"``).
    PLATAFORM_MANUAL : str, class attribute
        Identifier of the platform manual (``"Manual"``).
    VERSION : str, class attribute
        Application version shown in the status bar.
    DEFAULT_DATE_FORMAT : str, class attribute
        Date mask used when the language is not ``en_US``
        (``"%d/%m/%Y"``).
    DEFAULT_HOUR_FORMAT : str, class attribute
        Hour mask used when the language is not ``en_US``
        (``"%H:%M:%S"``).
    DEFAULT_HOUR_MINUTE_FORMAT : str, class attribute
        Hour-minute mask used when the language is not ``en_US``
        (``"%H:%M"``).
    SETTINGS_GERAL : str, class attribute
        Section of the general settings in the configuration file
        (``"geral"``).
    SETTINGS_GERAL_DATE_MASK : str, class attribute
        Settings key of the date mask.
    SETTINGS_GERAL_HOUR_MASK : str, class attribute
        Settings key of the hour mask.
    SETTINGS_GERAL_HOUR_MINUTE_MASK : str, class attribute
        Settings key of the hour-minute mask.
    SETTINGS_GERAL_LANGUAGE : str, class attribute
        Settings key of the language.
    SETTINGS_GERAL_VERSION : str, class attribute
        Settings key of the application version.
    USA_DATE_FORMAT : str, class attribute
        Date mask used for ``en_US`` (``"%m/%d/%Y"``).
    USA_HOUR_FORMAT : str, class attribute
        Hour mask used for ``en_US`` (``"%I:%M:%S %p"``).
    USA_HOUR_MINUTE_FORMAT : str, class attribute
        Hour-minute mask used for ``en_US`` (``"%I:%M %p"``).
    TRANSLATION_EXTENSION : str, class attribute
        Extension of the compiled Qt translation files (``".qm"``).

    Methods
    -------
    get_title()
        Return the translated application title.
    get_geral_date_mask()
        Return the date mask from the settings or by language.
    get_geral_hour_mask()
        Return the hour mask from the settings or by language.
    get_geral_hour_minute_mask()
        Return the hour-minute mask from the settings or by language.
    config_file_exists(filename=PathConfig.CONFIG_FILENAME)
        Check whether the configuration file exists.
    """

    ICON_APP: str = PathConfig.icon_system("appicon")
    LOGO_APP: str = PathConfig.image("ttealogo")
    PLATAFORM_SUFFIX: str = "TEA"
    PLATAFORM_MANUAL: str = "Manual"
    VERSION: str = "2.0"

    DEFAULT_DATE_FORMAT: str = "%d/%m/%Y"
    DEFAULT_HOUR_FORMAT: str = "%H:%M:%S"
    DEFAULT_HOUR_MINUTE_FORMAT: str = "%H:%M"
    SETTINGS_GERAL: str = "geral"
    SETTINGS_GERAL_DATE_MASK: str = f"{SETTINGS_GERAL}/date_mask"
    SETTINGS_GERAL_HOUR_MASK: str = f"{SETTINGS_GERAL}/hour_mask"
    SETTINGS_GERAL_HOUR_MINUTE_MASK: str = f"{SETTINGS_GERAL}/hour_minute_mask"
    SETTINGS_GERAL_LANGUAGE: str = f"{SETTINGS_GERAL}/language"
    SETTINGS_GERAL_VERSION: str = f"{SETTINGS_GERAL}/version"
    USA_DATE_FORMAT: str = "%m/%d/%Y"
    USA_HOUR_FORMAT: str = "%I:%M:%S %p"
    USA_HOUR_MINUTE_FORMAT: str = "%I:%M %p"
    TRANSLATION_EXTENSION: str = ".qm"

    @staticmethod
    def get_title() -> str:
        """Return the translated application title.

        Returns
        -------
        str
            The title, from the pt_BR source text "Plataforma T-TEA".

        Notes
        -----
        Translated at runtime with ``QCoreApplication.translate`` in the
        ``"TTeaApp"`` context, so it follows the installed translator.
        """
        return QCoreApplication.translate("TTeaApp", "Plataforma T-TEA")

    @staticmethod
    def get_geral_date_mask() -> str:
        """Return the date mask from the settings or by language.

        Returns
        -------
        str
            ``strftime`` mask for date display.

        Notes
        -----
        The value saved under ``geral/date_mask`` in the configuration
        file (``PathConfig.config()``) wins when it is not empty; it is
        set by ``LanguageService.apply_language``. Otherwise the mask is
        ``USA_DATE_FORMAT`` (``"%m/%d/%Y"``) when the current language
        is ``en_US`` and ``DEFAULT_DATE_FORMAT`` (``"%d/%m/%Y"``)
        otherwise.
        """
        from ttea.model import AppModel

        settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        saved_mask = settings.value(AppConfig.SETTINGS_GERAL_DATE_MASK)

        if saved_mask:  # Allow future manual override
            return saved_mask

        # Uses the current language, already validated
        # and with a fallback guaranteed by AppModel
        return (
            AppConfig.USA_DATE_FORMAT
            if AppModel().current_language == "en_US"
            else AppConfig.DEFAULT_DATE_FORMAT
        )

    @staticmethod
    def get_geral_hour_mask() -> str:
        """Return the hour mask from the settings or by language.

        Returns
        -------
        str
            ``strftime`` mask for hour display.

        Notes
        -----
        The value saved under ``geral/hour_mask`` in the configuration
        file (``PathConfig.config()``) wins when it is not empty.
        Otherwise the mask is ``USA_HOUR_FORMAT`` (``"%I:%M:%S %p"``)
        when the current language is ``en_US`` and
        ``DEFAULT_HOUR_FORMAT`` (``"%H:%M:%S"``) otherwise.
        """
        from ttea.model import AppModel

        settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        saved_mask = settings.value(AppConfig.SETTINGS_GERAL_HOUR_MASK)

        if saved_mask:  # Allow future manual override
            return saved_mask

        # Uses the current language, already validated
        # and with a fallback guaranteed by AppModel
        return (
            AppConfig.USA_HOUR_FORMAT
            if AppModel().current_language == "en_US"
            else AppConfig.DEFAULT_HOUR_FORMAT
        )

    @staticmethod
    def get_geral_hour_minute_mask() -> str:
        """Return the hour-minute mask from the settings or by language.

        Returns
        -------
        str
            ``strftime`` mask for hour-minute display.

        Notes
        -----
        The value saved under ``geral/hour_minute_mask`` in the
        configuration file (``PathConfig.config()``) wins when it is not
        empty; it is set by ``LanguageService.apply_language``.
        Otherwise the mask is ``USA_HOUR_MINUTE_FORMAT`` (``"%I:%M
        %p"``) when the current language is ``en_US`` and
        ``DEFAULT_HOUR_MINUTE_FORMAT`` (``"%H:%M"``) otherwise.
        """
        from ttea.model import AppModel

        settings = QSettings(PathConfig.config(), QSettings.IniFormat)
        saved_mask = settings.value(AppConfig.SETTINGS_GERAL_HOUR_MINUTE_MASK)

        if saved_mask:  # Allow future manual override
            return saved_mask

        # Uses the current language, already validated
        # and with a fallback guaranteed by AppModel
        return (
            AppConfig.USA_HOUR_MINUTE_FORMAT
            if AppModel().current_language == "en_US"
            else AppConfig.DEFAULT_HOUR_MINUTE_FORMAT
        )

    @staticmethod
    def config_file_exists(filename: str = PathConfig.CONFIG_FILENAME) -> bool:
        """Check whether the configuration file exists.

        Parameters
        ----------
        filename : str, optional
            Name of the configuration file. Default is
            ``PathConfig.CONFIG_FILENAME``.

        Returns
        -------
        bool
            True if the file exists, False otherwise.

        Notes
        -----
        Delegates to ``PathConfig.config_file_exists``, which also
        creates the user directories if needed.
        """
        return PathConfig.config_file_exists(filename)
