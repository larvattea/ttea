from PySide6.QtCore import QCoreApplication, QSettings

# Local module import
from udescjoinvilletteautil import PathConfig


class AppConfig:
    """Configuration class for application settings and paths.

    This class defines constants for application configuration, including
    paths to icons and logos, platform identifiers, version information,
    date formats, and settings keys. It relies on the `PathConfig` class
    for resolving file paths.

    Parameters
    ----------
    None

    Attributes
    ----------
    GAMES_APP : list
        List of supported game names, e.g., ["KarTEA"].
    ICON_APP : str
        Path to the application icon file (larva.ico), resolved by
        `PathConfig.icon`.
    LOGO_APP : str
        Path to the application logo file (ttealogo.png), resolved by
        `PathConfig.image`.
    PLATAFORM_SUFIX : str
        Suffix identifier for the platform, set to "TEA".
    PLATAFORM_MANUAL : str
        Identifier for the platform manual, set to "Manual".
    VERSION : str
        Current version of the application, set to "2.0".
    DEFAULT_DATE_FORMAT : str
        Default date format for the application, set to "%d/%m/%Y"
        (DD/MM/YYYY).
    SETTINGS_GERAL : str
        Base key for general settings, set to "geral".
    SETTINGS_GERAL_DATE_MASK : str
        Settings key for the date format mask, set to "geral/date_mask".
    SETTINGS_GERAL_LANGUAGE : str
        Settings key for the language preference, set to "geral/language".
    SETTINGS_GERAL_VERSION : str
        Settings key for the application version, set to "geral/version".
    USA_DATE_FORMAT : str
        Alternative date format for USA, set to "%m/%d/%Y" (MM/DD/YYYY).
    TRANSLATION_EXTENSION : str
        File extension for translation files, set to ".qm".

    Methods
    -------
    get_title()
        Get the translated title of the application.
    get_geral_date_mask()
        Retrieve the date mask from settings.
    convert_strftime_to_qt_format(strftime_mask)
        Convert a Python strftime date mask to Qt format.

    Notes
    -----
    - The `ICON_APP` and `LOGO_APP` attributes rely on the `PathConfig`
      class to resolve file paths for the icon and logo, respectively.
    - Date formats use Python's `strftime`/`strptime` syntax for
      consistency.
    - Settings keys are structured hierarchically (e.g.,
      "geral/date_mask") for use in configuration management.
    - The `.qm` extension is typically associated with Qt translation
      files.

    Examples
    --------
    Accessing the application icon path:
    >>> config = AppConfig()
    >>> print(config.ICON_APP)
    '/path/to/larva.ico'  # Path resolved by PathConfig

    Using the default date format:
    >>> from datetime import datetime
    >>> date_str = datetime.now().strftime(AppConfig.DEFAULT_DATE_FORMAT)
    >>> print(date_str)
    '15/07/2025'
    """

    GAMES_APP: list = [
        "KarTEA",
    ]

    ICON_APP: str = PathConfig.icon("larva.ico")
    LOGO_APP: str = PathConfig.image("ttealogo.png")
    PLATAFORM_SUFIX: str = "TEA"
    PLATAFORM_MANUAL: str = "Manual"
    VERSION: str = "2.0"

    DEFAULT_DATE_FORMAT: str = "%d/%m/%Y"
    SETTINGS_GERAL: str = "geral"
    SETTINGS_GERAL_DATE_MASK: str = f"{SETTINGS_GERAL}/date_mask"
    SETTINGS_GERAL_LANGUAGE: str = f"{SETTINGS_GERAL}/language"
    SETTINGS_GERAL_VERSION: str = f"{SETTINGS_GERAL}/version"
    USA_DATE_FORMAT: str = "%m/%d/%Y"
    TRANSLATION_EXTENSION: str = ".qm"

    @staticmethod
    def get_title() -> str:
        """Get the translated title of the application.

        Returns
        -------
        str
            The translated title of the T-TEA platform.

        Notes
        -----
        Uses QCoreApplication.translate to ensure the title is
        translated according to the current language settings.
        """
        return QCoreApplication.translate("TTeaApp", "Plataforma T-TEA")

    @staticmethod
    def get_geral_date_mask() -> str:
        """Retrieve the date mask from settings.

        Returns
        -------
        str
            The date mask stored in the configuration settings.

        Notes
        -----
        Reads the date mask from the configuration file (config.ini)
        using QSettings.
        """
        return QSettings(
            PathConfig.inifile("config.ini"), QSettings.IniFormat
        ).value(AppConfig.SETTINGS_GERAL_DATE_MASK)

    @staticmethod
    def convert_strftime_to_qt_format(strftime_mask):
        """Convert a Python strftime date mask to Qt format.

        Parameters
        ----------
        strftime_mask : str
            The Python strftime date format mask (e.g., "%d/%m/%Y").

        Returns
        -------
        str
            The equivalent Qt date format mask (e.g., "dd/MM/yyyy").
        """
        mask = strftime_mask.replace("%Y", "yyyy")
        mask = mask.replace("%y", "yy")
        mask = mask.replace("%m", "MM")
        mask = mask.replace("%d", "dd")
        return mask
