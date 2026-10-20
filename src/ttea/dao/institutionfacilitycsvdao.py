"""CSV persistence of institutions/facilities, one file each."""

import os
import re
from dataclasses import fields
from typing import Dict, List, Optional

import portalocker

from ttea.dao import DAO
from ttea.model import InstitutionFacility
from ttea.util import CSVHandler, PathConfig


class InstitutionFacilityCsvDAO(DAO[InstitutionFacility]):
    """DAO for InstitutionFacility entities, one CSV file per record.

    Persists each institution facility in its own CSV file named after
    its ID and sanitized name, and keeps all institution facilities in
    an in-memory cache loaded when the DAO is created.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV data.
    institutionfacilities : dict[int, InstitutionFacility]
        In-memory cache by ID.
    file_map : dict[int, str]
        CSV file path by ID.
    int_properties : list[str]
        Names of the ``InstitutionFacility`` fields typed ``int``.
    bool_properties : list[str]
        Names of the ``InstitutionFacility`` fields typed ``bool``.

    Notes
    -----
    Files are named ``<id>_<sanitized name>_institutionfacility.csv``
    and stored in the institution facility directory of ``PathConfig``.
    """

    def __init__(self) -> None:
        self.csv_handler = CSVHandler()
        self.institutionfacilities: Dict[int, InstitutionFacility] = {}
        self.file_map: Dict[int, str] = {}
        self.int_properties = [
            f.name for f in fields(InstitutionFacility) if f.type == int
        ]
        self.bool_properties = [
            f.name for f in fields(InstitutionFacility) if f.type == bool
        ]
        self.load_all_institutionfacilities()

    def generate_next_id(self) -> int:
        """Return the next available institution facility ID.

        Returns
        -------
        int
            The highest cached ID plus 1, or 1 if the cache is empty.
        """
        if not self.institutionfacilities:
            return 1
        return max(self.institutionfacilities.keys()) + 1

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

    def insert(self, obj: InstitutionFacility) -> int:
        """Insert a new institution facility and write its CSV file.

        Parameters
        ----------
        obj : InstitutionFacility
            The institution facility to persist. An ``id`` of 0 or less
            is replaced in place by ``generate_next_id()``.

        Returns
        -------
        int
            The institution facility ID on success, or 0 if ``obj`` is
            not valid or its ID already exists.
        """
        if not obj.is_valid():
            return 0

        if obj.id <= 0:
            obj.id = self.generate_next_id()

        if obj.id in self.institutionfacilities:
            return 0

        self.institutionfacilities[obj.id] = obj
        filename = self.get_filename(obj)
        self.file_map[obj.id] = filename
        self.write_with_lock(
            filename, obj.get_data(), InstitutionFacility.PROPERTIES
        )
        return obj.id

    def update(self, obj: InstitutionFacility) -> bool:
        """Update an existing institution facility and rewrite its file.

        Parameters
        ----------
        obj : InstitutionFacility
            The institution facility with updated values.

        Returns
        -------
        bool
            True if updated, False if ``obj`` is not valid or its ID is
            not cached.

        Notes
        -----
        If the file name changes (the name changed), the old file is
        renamed before being rewritten.
        """
        if not obj.is_valid() or obj.id not in self.institutionfacilities:
            return False

        old_filename = self.file_map.get(obj.id)
        new_filename = self.get_filename(obj)

        if old_filename != new_filename and os.path.exists(old_filename):
            os.rename(old_filename, new_filename)

        self.institutionfacilities[obj.id] = obj
        self.file_map[obj.id] = new_filename
        self.write_with_lock(
            new_filename, obj.get_data(), InstitutionFacility.PROPERTIES
        )
        return True

    def delete(self, obj_id: int) -> bool:
        """Delete an institution facility and remove its CSV file.

        Parameters
        ----------
        obj_id : int
            ID of the institution facility to delete.

        Returns
        -------
        bool
            True if deleted, False if the ID is not cached.
        """
        if obj_id not in self.institutionfacilities:
            return False

        filename = self.file_map.pop(obj_id, None)
        self.institutionfacilities.pop(obj_id, None)

        if filename and os.path.exists(filename):
            os.remove(filename)
        return True

    def select(self, obj_id: int) -> Optional[InstitutionFacility]:
        """Return an institution facility from the in-memory cache.

        Parameters
        ----------
        obj_id : int
            The institution facility ID to look up.

        Returns
        -------
        InstitutionFacility | None
            The institution facility, or None if the ID is not cached.
        """
        return self.institutionfacilities.get(obj_id)

    def list(self) -> List[InstitutionFacility]:
        """Return all cached institution facilities.

        Returns
        -------
        list[InstitutionFacility]
            The cached institution facilities, in cache order.
        """
        return list(self.institutionfacilities.values())

    def sanitize_filename(self, name: str) -> str:
        """Make an institution facility name safe for file names.

        Parameters
        ----------
        name : str
            Original name.

        Returns
        -------
        str
            The name stripped and lowercased, with every character that
            is not a word character or ``-`` replaced by ``_``.

        Examples
        --------
        >>> dao = object.__new__(InstitutionFacilityCsvDAO)
        >>> dao.sanitize_filename(" Ana Maria! ")
        'ana_maria_'
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, institutionfacility: InstitutionFacility) -> str:
        """Return the full path of an institution facility's CSV file.

        Parameters
        ----------
        institutionfacility : InstitutionFacility
            The institution facility.

        Returns
        -------
        str
            Path of ``<id>_<sanitized name>_institutionfacility.csv`` in
            the institution facility directory.
        """
        sanitized_name = self.sanitize_filename(institutionfacility.name)
        filename = f"{institutionfacility.id}_{sanitized_name}_institutionfacility.csv"
        return PathConfig.institutionfacility(filename)

    def load_all_institutionfacilities(self) -> None:
        """Load every institution facility CSV file into the cache.

        Notes
        -----
        Reads each ``*_institutionfacility.csv`` file of the institution
        facility directory; empty or unreadable files are skipped. Only
        the first row is used. Integer fields that are not plain digits
        (including negative numbers) become 0, and boolean fields are
        True only for ``"true"`` (any case).
        """
        PathConfig.ensure_dirs()
        for file_path in PathConfig.INSTITUTIONFACILITY_DIR.glob(
            "*_institutionfacility.csv"
        ):
            institutionfacility_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if not institutionfacility_data:
                continue

            row = institutionfacility_data[0]
            institutionfacility_kwargs = {}
            for prop in InstitutionFacility.PROPERTIES:
                if prop in row:
                    if prop in self.int_properties:
                        institutionfacility_kwargs[prop] = (
                            int(row[prop]) if row[prop].isdigit() else 0
                        )
                    elif prop in self.bool_properties:
                        institutionfacility_kwargs[prop] = (
                            row[prop].lower() == "true"
                        )
                    else:
                        institutionfacility_kwargs[prop] = row[prop]

            institutionfacility = InstitutionFacility(
                **institutionfacility_kwargs
            )
            self.institutionfacilities[institutionfacility.id] = (
                institutionfacility
            )
            self.file_map[institutionfacility.id] = str(file_path)

    def search_institutionfacilities(
        self, query: str = ""
    ) -> List[InstitutionFacility]:
        """Return cached institution facilities, optionally filtered.

        Parameters
        ----------
        query : str, optional
            Text searched, case-insensitively, in the ID and the name. A
            blank query returns every institution facility. Default is
            ``""``.

        Returns
        -------
        list[InstitutionFacility]
            The matching institution facilities.
        """
        all_institutionfacilities = list(self.institutionfacilities.values())

        if not query.strip():
            return all_institutionfacilities

        q = query.lower().strip()
        return [
            p
            for p in all_institutionfacilities
            if q in str(p.id) or q in p.name.lower()
        ]
