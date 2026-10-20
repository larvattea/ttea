"""Conversion helpers for Python date formats and Qt date widgets.

This module converts Python ``strftime`` masks to Qt date-format
strings and provides helpers for creating ``QDate`` objects from
Python date values.
"""

from datetime import date, datetime
from typing import Final

from PySide6.QtCore import QDate


class QtDateFormat:
    """Convert Python strftime date formats to Qt formats.

    Provides a clean separation between application configuration
    (strftime masks) and Qt presentation logic.

    Methods
    -------
    from_config() -> str
        Return the Qt date format of the current application setting.
    strftime_to_qt(strftime_mask) -> str
        Convert an arbitrary strftime mask to Qt syntax.
    format_python_date(python_date) -> str
        Format a Python date using the configured Qt mask.
    to_qdate(python_date) -> QDate
        Convert a Python date or datetime object to ``QDate``.

    Examples
    --------
    >>> QtDateFormat.strftime_to_qt('%d de %B de %Y')
    'dd de MMMM de yyyy'
    """

    @staticmethod
    def from_config() -> str:
        """Return the Qt date format of the application configuration.

        The configured mask uses Python ``strftime`` syntax
        (e.g. ``"%d/%m/%Y"``). This method returns the equivalent
        format string ready for Qt widgets.

        Returns
        -------
        str
            Format string suitable for ``QDateEdit.setDisplayFormat()``,
            ``QDateTimeEdit.setDisplayFormat()`` or
            ``QDate.toString()``.

        See Also
        --------
        strftime_to_qt : Low-level conversion function.

        Notes
        -----
        The mask is read from ``AppConfig.get_geral_date_mask()`` on
        every call.
        """
        from ttea.app import AppConfig

        strftime_mask = AppConfig.get_geral_date_mask()
        return QtDateFormat.strftime_to_qt(strftime_mask)

    @staticmethod
    def strftime_to_qt(strftime_mask: str) -> str:
        """Convert a Python ``strftime`` mask to Qt format syntax.

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

        Any other text, including other ``%`` directives, is kept
        unchanged and is not quoted. Qt reads unquoted letters such as
        ``d``, ``M`` and ``y`` as format characters, so the literal
        "de" in ``"%d de %B de %Y"`` is shown by Qt as the day number
        followed by "e". TODO(doc): should literal text be quoted
        (``'de'``) in the Qt mask?

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

    @staticmethod
    def format_python_date(python_date: date | datetime | None) -> str:
        """Format a Python date object using the configured Qt mask.

        Parameters
        ----------
        python_date : date | datetime | None
            Python date or datetime object to format.

        Returns
        -------
        str
            Formatted date string according to ``from_config()``, or an
            empty string when ``python_date`` is None.

        Notes
        -----
        Only the date part is used; the time of a ``datetime`` is
        ignored.
        """
        if python_date is None:
            return ""
        qt_mask = QtDateFormat.from_config()
        q_date = QDate(python_date.year, python_date.month, python_date.day)

        return q_date.toString(qt_mask)

    @staticmethod
    def to_qdate(python_date: date | datetime | None) -> QDate:
        """Convert a Python date or datetime object to ``QDate``.

        Parameters
        ----------
        python_date : date | datetime | None
            Python date or datetime object to convert.

        Returns
        -------
        QDate
            Corresponding Qt date, or the current date when
            ``python_date`` is None or falsy.

        Examples
        --------
        >>> from datetime import date
        >>> qdate = QtDateFormat.to_qdate(date(2024, 1, 5))
        >>> qdate.toString("yyyy-MM-dd")
        '2024-01-05'
        >>> QtDateFormat.to_qdate(None) == QDate.currentDate()
        True
        """
        if not python_date:
            return QDate.currentDate()

        return QDate(python_date.year, python_date.month, python_date.day)
