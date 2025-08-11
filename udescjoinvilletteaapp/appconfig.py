from PySide6.QtCore import QCoreApplication

# Local module import
from udescjoinvilletteautil import PathConfig


class AppConfig:
    """Configuration class for application settings and paths.

    This class defines constants for application configuration, including
    paths to icons and logos, platform identifiers, version information,
    date formats, and settings keys.
    It relies on the `PathConfig` class for resolving file paths.

    Attributes
    ----------
    ICON_APP : str
        Path to the application icon file (larva.ico), resolved
        using `PathConfig.icon`.
    LOGO_APP : str
        Path to the application logo file (ttealogo.png), resolved
        using `PathConfig.image`.
    PLATAFORM_SUFIX : str
        Suffix identifier for the platform, set to "TEA".
    PLATAFORM_MANUAL : str
        Identifier for the platform manual, set to "Manual".
    VERSION : str
        Current version of the application, set to "2.0".
    DEFAULT_DATE_FORMAT : str
        Default date format for the application,
        set to "%d/%m/%Y" (DD/MM/YYYY).
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

    Notes
    -----
    - The `ICON_APP` and `LOGO_APP` attributes rely on the `PathConfig` class
      to resolve file paths for the icon and logo, respectively.
    - Date formats use Python's `strftime`/`strptime` syntax for consistency.
    - Settings keys are structured hierarchically (e.g., "geral/date_mask")
      for use in configuration management.
    - The `.qm` extension is typically associated with Qt translation files.

    Examples
    --------
    Accessing the application icon path:
    >>> config = AppConfig()
    >>> print(config.ICON_APP)
    '/path/to/larva.ico'  # Path resolved by PathConfig.icon

    Using the default date format:
    >>> from datetime import datetime
    >>> date_str = datetime.now().strftime(AppConfig.DEFAULT_DATE_FORMAT)
    >>> print(date_str)
    '15/07/2025'
    """

    ICON_APP = PathConfig.icon("larva.ico")
    LOGO_APP = PathConfig.image("ttealogo.png")
    PLATAFORM_SUFIX = "TEA"
    PLATAFORM_MANUAL = "Manual"
    VERSION = "2.0"

    DEFAULT_DATE_FORMAT = "%d/%m/%Y"
    SETTINGS_GERAL = "geral"
    SETTINGS_GERAL_DATE_MASK = f"{SETTINGS_GERAL}/date_mask"
    SETTINGS_GERAL_LANGUAGE = f"{SETTINGS_GERAL}/language"
    SETTINGS_GERAL_VERSION = f"{SETTINGS_GERAL}/version"
    USA_DATE_FORMAT = "%m/%d/%Y"
    TRANSLATION_EXTENSION = ".qm"

    @staticmethod
    def get_title() -> str:
        """Get the translated title of the application.

        Returns
        -------
        str
            The translated title of the T-TEA platform.

        Notes
        -----
        Uses QCoreApplication.translate to ensure the title is translated
        according to the current language settings.
        """
        return QCoreApplication.translate("TTeaApp", "Plataforma T-TEA")
