import csv
from typing import Dict, List, Optional, Union


class CSVHandler:
    """A class for handling CSV files with a custom dialect.

    Attributes
    ----------
    dialect : str, optional
        The CSV dialect to use (default: 'excel').
    delimiter : str, optional
        The character used as a field delimiter (default: ';').
    quotechar : str, optional
        The character used for quoting fields (default: '"').
    doublequote : bool, optional
        Whether to escape quotes by doubling them (default: True).
    skipinitialspace : bool, optional
        Whether to skip initial whitespace after delimiters (default: True).
    lineterminator : str, optional
        The character used to terminate lines (default: '\n').
    quoting : int, optional
        The quoting style for fields (default: csv.QUOTE_MINIMAL).

    Methods:
    __init__(dialect, delimiter, quotechar, doublequote, skipinitialspace,
        lineterminator, quoting):
        Initialize the CSVHandler with custom dialect settings.
    write_csv(filename, data, headers):
        Write data to a CSV file.
    read_csv(filename, as_dict):
        Read data from a CSV file.

    Notes
    -----
    - The class registers a custom CSV dialect upon initialization using the
    provided parameters.
    - This dialect is used for all read and write operations.
    """

    def __init__(
        self,
        dialect: str = "excel",
        delimiter: str = ";",
        quotechar: str = '"',
        doublequote: bool = True,
        skipinitialspace: bool = True,
        lineterminator: str = "\n",
        quoting: int = csv.QUOTE_MINIMAL,
    ) -> None:
        """Initialize the CSVHandler with custom dialect settings.

        Parameters
        ----------
        dialect : str, optional
            The CSV dialect to use (default: 'excel').
        delimiter : str, optional
            The character used as a field delimiter (default: ';').
        quotechar : str, optional
            The character used for quoting fields (default: '"').
        doublequote : bool, optional
            Whether to escape quotes by doubling them (default: True).
        skipinitialspace : bool, optional
            Whether to skip initial whitespace after delimiters
            (default: True).
        lineterminator : str, optional
            The character used to terminate lines (default: '\n').
        quoting : int, optional
            The quoting style for fields (default: csv.QUOTE_MINIMAL).

        Returns
        -------
        None

        Notes
        -----
        Registers the specified dialect with the `csv` module for use in
        read/write operations.
        """
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

    def write_csv(
        self,
        filename: str,
        data: List[Union[Dict, List]],
        headers: Optional[List[str]] = None,
    ) -> None:
        """Write data to a CSV file.

        Parameters
        ----------
        filename : str
            The name of the CSV file to write to.
        data : List[Union[Dict, List]]
            A list of dictionaries or lists containing the data to write.
        headers : Optional[List[str]], optional
            A list of header names for the CSV file (default: None).


        Returns
        -------
        None

        Notes
        -----
        - If `headers` is provided, the data is expected to be a list of
        dictionaries,
          and a header row is written to the CSV file.
        - If `headers` is None, the data is treated as a list of lists, and no
        header row is written.
        - The file is written with UTF-8 encoding and uses the custom dialect.
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            if headers:
                writer = csv.DictWriter(
                    file, fieldnames=headers, dialect=self.dialect
                )
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            else:
                writer = csv.writer(file, dialect=self.dialect)
                for row in data:
                    writer.writerow(row)

    def read_csv(
        self, filename: str, as_dict: bool = False
    ) -> List[Union[Dict, List]]:
        """Read data from a CSV file.

        Parameters
        ----------
        filename : str
            The name of the CSV file to read from.
        as_dict : bool, optional
            If True, returns data as a list of dictionaries; otherwise,
            as a list of lists (default: False).

        Returns
        -------
        List[Union[Dict, List]]
            A list of rows from the CSV file, either as dictionaries
            (if `as_dict=True`) or as lists (if `as_dict=False`).

        Notes
        -----
        - The file is read with UTF-8 encoding and uses the custom dialect.
        - If the file cannot be read, an empty list is returned.
        """
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            if as_dict:
                reader = csv.DictReader(file, dialect=self.dialect)
            else:
                reader = csv.reader(file, dialect=self.dialect)
            return list(reader)
        return []
