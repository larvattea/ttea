"""CSV persistence of the calibration corner points."""

from dataclasses import fields
from typing import Dict, List, Optional

import portalocker

from ttea.model import CalibrationPoint
from ttea.util import CSVHandler, PathConfig

# Import DAO directly to avoid a circular import
from .dao import DAO


class CalibrationPointCsvDAO(DAO[CalibrationPoint]):
    """DAO for the single ``CalibrationPoint`` record in a CSV file.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV data.
    calibration_points : dict[int, CalibrationPoint]
        In-memory cache by ID (at most one entry).
    file_map : dict[int, str]
        CSV file path by ID.
    int_properties : list[str]
        Names of the ``CalibrationPoint`` fields typed ``int``.

    Notes
    -----
    The record is stored in ``PathConfig.calibration_point()`` with ID
    ``CalibrationPoint.ID_VALUE`` and loaded into the cache when the DAO
    is created. ``update``, ``delete`` and ``list`` are not implemented
    and raise ``NotImplementedError``.
    """

    def __init__(self) -> None:
        self.csv_handler = CSVHandler()
        self.calibration_points: Dict[int, CalibrationPoint] = {}
        self.file_map: Dict[int, str] = {}
        self.int_properties = [
            f.name for f in fields(CalibrationPoint) if f.type == int
        ]

        self.load_all_calibration_points()

    def write_with_lock(
        self, filepath: str, data: List[Dict], headers: List[str]
    ):
        """Write rows to a CSV file while holding an exclusive lock.

        Parameters
        ----------
        filepath : str
            Full path to the target CSV file.
        data : list[dict]
            Rows to write, one dictionary per row.
        headers : list[str]
            Ordered column names; a header row is written first.

        Raises
        ------
        portalocker.exceptions.LockException
            If the lock cannot be acquired within 10 seconds.

        Notes
        -----
        The user directories are created if needed. The file is opened
        by ``portalocker.Lock`` in mode ``"w"`` with Python's defaults,
        so it uses the platform's default encoding and newline
        translation, unlike ``CSVHandler.write_csv`` with a path (UTF-8
        with BOM).
        """
        PathConfig.ensure_dirs()
        with portalocker.Lock(filepath, mode="w", timeout=10) as f:
            self.csv_handler.write_csv(f, data, headers)

    def insert(self, obj: CalibrationPoint) -> int:
        """Save the calibration points, replacing the previous ones.

        Parameters
        ----------
        obj : CalibrationPoint
            The points to save. They are not validated.

        Returns
        -------
        int
            ``CalibrationPoint.ID_VALUE``.
        """
        self.calibration_points[CalibrationPoint.ID_VALUE] = obj
        filename = PathConfig.calibration_point(
            PathConfig.CALIBRATION_POINT_FILENAME
        )
        self.file_map[CalibrationPoint.ID_VALUE] = filename
        self.write_with_lock(
            filename, obj.get_data(), CalibrationPoint.PROPERTIES
        )
        return CalibrationPoint.ID_VALUE

    def update(self, obj: CalibrationPoint) -> bool:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def delete(self, obj_id: int) -> bool:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def select(self, obj_id: int) -> Optional[CalibrationPoint]:
        """Return the calibration points from the in-memory cache.

        Parameters
        ----------
        obj_id : int
            The record ID, normally ``CalibrationPoint.ID_VALUE``.

        Returns
        -------
        CalibrationPoint | None
            The cached points, or None if none were loaded or saved.
        """
        return self.calibration_points.get(obj_id)

    def list(self) -> List[CalibrationPoint]:
        """Not implemented.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError

    def load_all_calibration_points(self) -> None:
        """Load the calibration point CSV file into the cache.

        Notes
        -----
        Only the first row of the file is used. Coordinates that are not
        plain digits, including negative numbers, are loaded as 0.
        """
        PathConfig.ensure_dirs()
        for file_path in PathConfig.CALIBRATION_DIR.glob(
            PathConfig.CALIBRATION_POINT_FILENAME
        ):
            calibration_point_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if not calibration_point_data:
                continue

            row = calibration_point_data[0]
            calibration_point_kwargs = {}
            for prop in CalibrationPoint.PROPERTIES:
                if prop in row:
                    if prop in self.int_properties:
                        calibration_point_kwargs[prop] = (
                            int(row[prop]) if row[prop].isdigit() else 0
                        )
                    else:
                        calibration_point_kwargs[prop] = row[prop]

            calibration_point = CalibrationPoint(**calibration_point_kwargs)
            self.calibration_points[calibration_point.ID_VALUE] = (
                calibration_point
            )
            self.file_map[calibration_point.ID_VALUE] = str(file_path)
