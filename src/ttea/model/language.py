"""Language model: the languages supported by the application."""

from typing import Dict, List

from ttea.util import PathConfig


class Language:
    """Static data of the languages supported by the application.

    Attributes
    ----------
    LANGUAGES : list[dict[str, str]], class attribute
        Available languages, each with ``"code"`` (e.g. ``"pt_BR"``),
        ``"description"`` (the language name in that language) and
        ``"flag"`` (Qt resource path of the flag icon).
    DEFAULT_LANGUAGE : str, class attribute
        Language used when no valid language is set (``"pt_BR"``).

    Examples
    --------
    >>> [lang["code"] for lang in Language().get_languages()]
    ['pt_BR', 'es_ES', 'en_US']
    """

    LANGUAGES = [
        {
            "code": "pt_BR",
            "description": "Português",
            "flag": PathConfig.flag("brazil"),
        },
        {
            "code": "es_ES",
            "description": "Español",
            "flag": PathConfig.flag("spain"),
        },
        {
            "code": "en_US",
            "description": "English",
            "flag": PathConfig.flag("usa"),
        },
    ]

    DEFAULT_LANGUAGE = "pt_BR"

    def get_languages(self) -> List[Dict[str, str]]:
        """Return the list of available languages.

        Returns
        -------
        list[dict[str, str]]
            ``LANGUAGES`` itself (not a copy).
        """
        return self.LANGUAGES
