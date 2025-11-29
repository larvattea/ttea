# udescjoinvilletteautil/qtdateformat.py
from typing import Final


class QtDateFormat:
    """
    Utility for converting Python strftime date formats to Qt-compatible formats.

    Provides a clean separation between application configuration
    (strftime masks) and Qt presentation logic.

    Methods
    -------
    from_config() -> str
        Return the Qt date format based on the current application setting.
    strftime_to_qt(strftime_mask) -> str
        Convert an arbitrary strftime mask to Qt syntax.

    Examples
    --------
    >>> QtDateFormat.from_config()
    'dd/MM/yyyy'

    >>> QtDateFormat.strftime_to_qt('%d de %B de %Y')
    'dd de MMMM de yyyy'
    """

    @staticmethod
    def from_config() -> str:
        """
        Return the Qt date-format mask defined in the application
        configuration.

        The configured mask uses Python ``strftime`` syntax
        (e.g. ``"%d/%m/%Y"``). This method returns the equivalent
        format string ready for Qt widgets.

        Returns
        -------
        str
            Format string suitable for ``QDateEdit.setDisplayFormat()``,
            ``QDateTimeEdit.setDisplayFormat()`` or ``QDate.toString()``.

        See Also
        --------
        strftime_to_qt : low-level conversion function.
        """
        # Local module import
        from udescjoinvilletteaapp import AppConfig

        strftime_mask = AppConfig.get_geral_date_mask()
        return QtDateFormat.strftime_to_qt(strftime_mask)

    @staticmethod
    def strftime_to_qt(strftime_mask: str) -> str:
        """
        Convert a Python ``strftime`` format string to Qt format syntax.

        Parameters
        ----------
        strftime_mask : str
            Date format using ``strftime`` directives, e.g.
            ``"%d/%m/%Y"``, ``"%Y-%m-%d"`` or ``"%d de %B de %Y"``.

        Returns
        -------
        str
            Equivalent format string understood by Qt.

        Notes
        -----
        Supported ``strftime`` to Qt mappings:

        ===========  =======  ==================================
        strftime     Qt       Description
        ===========  =======  ==================================
        %Y           yyyy     4-digit year
        %y           yy       2-digit year
        %m           MM       Month as zero-padded number (01-12)
        %d           dd       Day as zero-padded number (01-31)
        %B           MMMM     Full month name
        %b           MMM      Abbreviated month name
        %A           dddd     Full weekday name
        %a           ddd      Abbreviated weekday name
        ===========  =======  ==================================

        All literal characters (slashes, dashes, spaces, words like "de",
        commas, etc.) are preserved unchanged.

        Examples
        --------
        >>> QtDateFormat.strftime_to_qt("%d/%m/%Y")
        'dd/MM/yyyy'

        >>> QtDateFormat.strftime_to_qt("%Y-%m-%d")
        'yyyy-MM-dd'

        >>> QtDateFormat.strftime_to_qt("%d de %B de %Y")
        'dd de MMMM de yyyy'

        >>> QtDateFormat.strftime_to_qt("%a, %d %b %Y")
        'ddd, dd MMM yyyy'
        """
        _replacements: Final[dict[str, str]] = {
            "%Y": "yyyy",
            "%y": "yy",
            "%m": "MM",
            "%d": "dd",
            "%B": "MMMM",
            "%b": "MMM",
            "%A": "dddd",
            "%a": "ddd",
        }

        qt_mask = strftime_mask
        for py_token, qt_token in _replacements.items():
            qt_mask = qt_mask.replace(py_token, qt_token)

        return qt_mask
