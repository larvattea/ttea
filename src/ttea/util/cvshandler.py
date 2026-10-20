"""CSV file handling utilities for the T-TEA platform.

This module provides the ``CSVHandler`` class for reading and
writing CSV files with a custom dialect and robust error handling.
"""

import csv
import io
import locale
import os
from pathlib import Path
from typing import Dict, List, Optional, TextIO, Union


class CSVHandler:
    r"""Read and write CSV files with a custom dialect.

    Fully integrated with the application's singleton logger. Works
    with file paths or already-opened file-like objects (e.g. locked
    via portalocker). Handles common real-world issues: file locked by
    Excel, wrong encoding, corrupted files, missing directories,
    permission errors, etc.

    Parameters
    ----------
    dialect : str, optional
        Name of the CSV dialect to register and use. Default is
        ``"custom_ttea"``.
    delimiter : str, optional
        Field delimiter character. Default is ``";"``.
    quotechar : str, optional
        Character used to quote fields containing special
        characters. Default is ``'"'``.
    doublequote : bool, optional
        Whether a ``quotechar`` inside a field is doubled. Default is
        True.
    skipinitialspace : bool, optional
        When True, whitespace immediately following the delimiter is
        ignored. Default is True.
    lineterminator : str, optional
        String used to terminate lines produced by the writer.
        Default is a newline (``"\n"``).
    quoting : int, optional
        Quoting policy (one of the ``csv.QUOTE_*`` constants).
        Default is ``csv.QUOTE_MINIMAL``.

    Attributes
    ----------
    dialect : str
        Registered CSV dialect name.
    log : Log
        Singleton logger instance used by the handler.

    Methods
    -------
    write_csv(file_or_path, data, headers=None)
        Write data to a CSV file or an already-opened file object.
    read_csv(filename=None, as_dict=False, content=None)
        Read CSV data safely, returning an empty list on any error.

    Notes
    -----
    The dialect is registered with ``csv.register_dialect`` on every
    instantiation, replacing any dialect with the same name.

    Examples
    --------
    >>> handler = CSVHandler()  # doctest: +SKIP
    >>> handler.read_csv(content="a;b\n1;2")  # doctest: +SKIP
    [['a', 'b'], ['1', '2']]
    """

    def __init__(
        self,
        dialect: str = "custom_ttea",  # custom dialect name to avoid conflicts
        delimiter: str = ";",
        quotechar: str = '"',
        doublequote: bool = True,
        skipinitialspace: bool = True,
        lineterminator: str = "\n",
        quoting: int = csv.QUOTE_MINIMAL,
    ) -> None:
        from ttea.log import Log

        csv.register_dialect(
            dialect,
            delimiter=delimiter,
            quotechar=quotechar,
            doublequote=doublequote,
            skipinitialspace=skipinitialspace,
            lineterminator=lineterminator,
            quoting=quoting,
        )
        self.dialect = dialect
        self.log = Log.get_log()

    def write_csv(
        self,
        file_or_path: Union[str, os.PathLike, TextIO],
        data: List[Union[Dict, List]],
        headers: Optional[List[str]] = None,
    ) -> None:
        """Write a list of rows or dictionaries to CSV.

        Works with a file path or an already-opened file-like object
        (e.g. locked with portalocker).

        Parameters
        ----------
        file_or_path : str | os.PathLike | TextIO
            Destination file path or an open file object.
        data : list[dict | list]
            Rows to write. Dictionaries require ``headers``.
        headers : list[str] | None, optional
            Field names when writing dictionaries. If provided, a header
            row is written first. Default is None.

        Raises
        ------
        Exception
            Any error while opening or writing is logged and re-raised.

        Notes
        -----
        With a path, parent directories are created if needed and the
        file is written in UTF-8 with BOM (``utf-8-sig``), so Excel
        detects the encoding. With an open file object, the caller is
        responsible for its mode, encoding and ``newline=""``.
        """
        if isinstance(file_or_path, (str, os.PathLike)):
            path = Path(file_or_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(path, "w", newline="", encoding="utf-8-sig") as f:
                    self._write_to_file(f, data, headers)
                # self.log.log_info(f"CSV saved successfully: {path.name}")
            except Exception as e:
                self.log.log_error(f"Failed to save CSV {path}: {e}")
                raise
        else:
            # File already open (e.g., portalocker.Lock)
            try:
                self._write_to_file(file_or_path, data, headers)
                # The file name is unknown here, so it is not logged.
            except Exception as e:
                self.log.log_error(f"Failed to write to locked CSV file: {e}")
                raise

    def _write_to_file(
        self,
        file: TextIO,
        data: List[Union[Dict, List]],
        headers: Optional[List[str]],
    ) -> None:
        """Write rows to an open file with the registered dialect.

        Internal helper of ``write_csv``. It assumes the file is open in
        text mode with the proper encoding and ``newline=""``.

        Parameters
        ----------
        file : TextIO
            Open file object ready for writing.
        data : list[dict | list]
            Data rows to write.
        headers : list[str] | None
            Field names for ``csv.DictWriter`` (a header row is
            written), or None to write plain rows with ``csv.writer``.
        """
        if headers:
            writer = csv.DictWriter(
                file, fieldnames=headers, dialect=self.dialect
            )
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(file, dialect=self.dialect)
            writer.writerows(data)

    def read_csv(
        self,
        filename: Optional[Union[str, os.PathLike]] = None,
        as_dict: bool = False,
        content: Optional[str] = None,
    ) -> List[Union[Dict, List]]:
        r"""Read CSV data with comprehensive error handling.

        Returns an empty list instead of raising exceptions for any
        problem (file missing, locked by Excel, wrong encoding,
        corrupted, etc.), so CSV issues never crash the application.

        Parameters
        ----------
        filename : str | os.PathLike | None, optional
            Path to the CSV file. Default is None.
        as_dict : bool, optional
            If True, return a list of dictionaries using the first row
            as keys. Default is False.
        content : str | None, optional
            CSV content provided directly as a string. Default is None.

        Returns
        -------
        list[dict] | list[list[str]]
            Rows as dictionaries if ``as_dict`` is True, otherwise as
            lists. Empty list on any read error.

        Notes
        -----
        If ``content`` is provided, ``filename`` is ignored; otherwise
        ``filename`` must be given.

        A missing file is logged at INFO level (normal on the first
        run). Encodings are tried in order: ``utf-8-sig``, the system's
        preferred encoding (if not already listed), ``cp1252``,
        ``utf-8`` and ``latin1``. A ``PermissionError`` (file locked,
        e.g. open in Excel) is logged as a warning; other read errors
        and a file that no encoding can decode are logged as errors.

        Examples
        --------
        >>> h = CSVHandler()  # doctest: +SKIP
        >>> rows = "a;b\n1;2"
        >>> h.read_csv(content=rows, as_dict=True)  # doctest: +SKIP
        [{'a': '1', 'b': '2'}]
        """
        if content is not None:
            try:
                f = io.StringIO(content)
                if as_dict:
                    reader = csv.DictReader(f, dialect=self.dialect)
                else:
                    reader = csv.reader(f, dialect=self.dialect)
                return list(reader)
            except Exception as e:
                self.log.log_error(f"Error reading CSV content: {e}")
                return []

        path = Path(filename)

        if not path.exists():
            self.log.log_info(
                f"CSV file does not exist (normal on first run): {path.name}"
            )
            return []

        # Order tested with pt-BR/pt-PT, Spanish and English files on
        # Windows, Linux and macOS.
        system_enc = locale.getpreferredencoding(False)
        encodings_to_try = ["utf-8-sig", "cp1252", "utf-8", "latin1"]

        if system_enc.lower() not in [e.lower() for e in encodings_to_try]:
            encodings_to_try.insert(1, system_enc)

        for encoding in encodings_to_try:
            try:
                with open(path, "r", newline="", encoding=encoding) as file:

                    if as_dict:
                        reader = csv.DictReader(file, dialect=self.dialect)
                    else:
                        reader = csv.reader(file, dialect=self.dialect)

                    rows = list(reader)
                    return rows
            except PermissionError:
                self.log.log_warning(
                    f"CSV file locked (probably open in Excel): {path.name}"
                )
                return []
            except UnicodeDecodeError:
                continue
            except (OSError, csv.Error) as e:
                self.log.log_error(
                    f"Error reading CSV {path.name} with {encoding}: {type(e).__name__}: {e}"
                )
                return []
        self.log.log_error(
            f"Could not decode CSV {path.name}. "
            f"Encodings tried: {', '.join(encodings_to_try)}"
        )
        return []
