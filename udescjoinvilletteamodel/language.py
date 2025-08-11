import ctypes
import locale
import os
import platform
from typing import Dict, List, Optional

# Local module import
from udescjoinvilletteautil import PathConfig


class Language:
    """Model for managing language data.

    This class handles information related to languages, including the list of
    available languages, the user-selected language, and retrieving
    the operating system's language.

    Attributes
    ----------
    LANGUAGES : List[Dict[str, str]]
        List of dictionaries containing information about available languages.
        Each dictionary has the keys:
        - code: Language code in the format 'language_COUNTRY' (e.g., 'pt_BR').
        - description: Language name (e.g., 'Português').
        - flag: Path to the flag image, obtained via PathConfig.
    DEFAULT_LANGUAGE : str
        Default language code used in case of failure ('pt_BR').
    selected_language : Optional[str]
        Code of the currently selected language by the user. Initially None.

    Methods
    -------
    get_languages()
        Returns the list of available languages.
    set_selected_language(language_code)
        Sets the selected language.
    get_selected_language()
        Returns the selected language.
    get_system_language()
        Retrieves the operating system's language.
    """

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

    def __init__(self) -> None:
        """Initializes the Language class instance.

        Sets the `selected_language` attribute to None.

        Returns
        -------
        None
        """
        self.selected_language: Optional[str] = None

    def get_languages(self) -> List[Dict[str, str]]:
        """Returns the list of available languages.

        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries containing available languages, with keys
            'code', 'description', and 'flag'.

        Examples
        --------
        >>> lang = Language()
        >>> lang.get_languages()
        [
            {'code': 'pt_BR', 'description': 'Português',
            'flag': '.../brazil.png'},
            {'code': 'en_US', 'description': 'English', 'flag': '.../usa.png'}
        ]
        """
        return self.LANGUAGES

    def set_selected_language(self, language_code: str) -> None:
        """Sets the selected language.

        Parameters
        ----------
        language_code : str
            Code of the language to be set (e.g., 'pt_BR', 'en_US').

        Returns
        -------
        None

        Notes
        -----
        Does not validate if the language code is valid. Ensure that the
        `language_code` is present in the list of available languages
        (`LANGUAGES`).

        Examples
        --------
        >>> lang = Language()
        >>> lang.set_selected_language('en_US')
        >>> lang.get_selected_language()
        'en_US'
        """
        self.selected_language = language_code

    def get_selected_language(self) -> Optional[str]:
        """Returns the selected language.

        Returns
        -------
        Optional[str]
            Code of the selected language or None if no language is set.

        Examples
        --------
        >>> lang = Language()
        >>> lang.get_selected_language()
        None
        >>> lang.set_selected_language('pt_BR')
        >>> lang.get_selected_language()
        'pt_BR'
        """
        return self.selected_language

    def get_system_language(self) -> str:
        """Retrieves the operating system's language in the format
        'language-COUNTRY'.

        Attempts to obtain the system language using `locale.getlocale()`.
        If unsuccessful, uses platform-specific methods for Windows or Linux.
        If all approaches fail, returns 'en-US' as the default.

        Returns
        -------
        str
            Language code in the format 'language-COUNTRY'
            (e.g., 'pt-BR', 'en-US').

        Notes
        -----
        - On Windows systems, uses the `ctypes` API to query the user's
        language.
        - On Linux systems, checks environment variables `LC_ALL`,
        `LC_MESSAGES`, and `LANG`.
        - Replaces underscores (_) with hyphens (-) to maintain the
          'language-COUNTRY' format.

        Examples
        --------
        >>> lang = Language()
        >>> lang.get_system_language()  # Assuming the system is set to pt_BR
        'pt-BR'
        """
        system_locale = locale.getlocale()[0]
        if system_locale:
            return system_locale.replace("_", "-")

        os_name = platform.system()
        if os_name == "Windows":

            windll = ctypes.windll.kernel32
            locale_id = windll.GetUserDefaultUILanguage()
            return locale.windows_locale.get(locale_id, "en-US")

        if os_name == "Linux":
            for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
                lang = os.getenv(env_var)
                if lang:
                    return lang.split(".")[0].replace("_", "-")

        return "en-US"
