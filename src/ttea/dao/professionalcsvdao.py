"""CSV persistence of professionals, one file per professional."""

import os
import re
from dataclasses import fields
from typing import TYPE_CHECKING, Dict, List, Optional

import portalocker

from ttea.dao import DAO
from ttea.model import Professional
from ttea.util import CSVHandler, PathConfig

if TYPE_CHECKING:
    from ttea.dao import InstitutionFacilityCsvDAO


class ProfessionalCsvDAO(DAO[Professional]):
    """DAO for Professional entities, one CSV file per record.

    Persists each professional in its own CSV file named after its ID
    and sanitized name, and keeps all professionals in an in-memory
    cache loaded when the DAO is created.

    Parameters
    ----------
    institution_dao : InstitutionFacilityCsvDAO | None, optional
        DAO used to resolve the institution of each professional.
        Default is None, which creates a new
        ``InstitutionFacilityCsvDAO`` (with its own cache).

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV data.
    professionals : dict[int, Professional]
        In-memory cache by ID.
    file_map : dict[int, str]
        CSV file path by ID.
    int_properties : list[str]
        Names of the ``Professional`` fields typed ``int``.
    bool_properties : list[str]
        Names of the ``Professional`` fields typed ``bool``.
    institution_dao : InstitutionFacilityCsvDAO
        DAO used to resolve institutions.

    Notes
    -----
    Files are named ``<id>_<sanitized name>_professional.csv`` and
    stored in the professional directory of ``PathConfig``.

    The ``institutionfacility`` column holds the facility ID. When
    loading, it is resolved with ``institution_dao.select``; an empty,
    non-numeric or unknown ID gives None, and such a professional is not
    valid until a facility is set.
    """

    def __init__(
        self, institution_dao: Optional["InstitutionFacilityCsvDAO"] = None
    ) -> None:
        from ttea.dao import InstitutionFacilityCsvDAO

        self.csv_handler = CSVHandler()
        self.professionals: Dict[int, Professional] = {}
        self.file_map: Dict[int, str] = {}
        self.int_properties = [
            f.name for f in fields(Professional) if f.type == int
        ]
        self.bool_properties = [
            f.name for f in fields(Professional) if f.type == bool
        ]
        self.institution_dao = institution_dao or InstitutionFacilityCsvDAO()
        self.load_all_professionals()

    def generate_next_id(self) -> int:
        """Return the next available professional ID.

        Returns
        -------
        int
            The highest cached ID plus 1, or 1 if the cache is empty.
        """
        if not self.professionals:
            return 1
        return max(self.professionals.keys()) + 1

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

    def insert(self, obj: Professional) -> int:
        """Insert a new professional and write its CSV file.

        Parameters
        ----------
        obj : Professional
            The professional to persist. An ``id`` of 0 or less is
            replaced in place by ``generate_next_id()``.

        Returns
        -------
        int
            The professional ID on success, or 0 if ``obj`` is not valid
            or its ID already exists.
        """
        if not obj.is_valid():
            return 0

        if obj.id <= 0:
            obj.id = self.generate_next_id()

        if obj.id in self.professionals:
            return 0

        self.professionals[obj.id] = obj
        filename = self.get_filename(obj)
        self.file_map[obj.id] = filename
        self.write_with_lock(filename, obj.get_data(), Professional.PROPERTIES)
        return obj.id

    def update(self, obj: Professional) -> bool:
        """Update an existing professional and rewrite its file.

        Parameters
        ----------
        obj : Professional
            The professional with updated values.

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
        if not obj.is_valid() or obj.id not in self.professionals:
            return False

        old_filename = self.file_map.get(obj.id)
        new_filename = self.get_filename(obj)

        if old_filename != new_filename and os.path.exists(old_filename):
            os.rename(old_filename, new_filename)

        self.professionals[obj.id] = obj
        self.file_map[obj.id] = new_filename
        self.write_with_lock(
            new_filename, obj.get_data(), Professional.PROPERTIES
        )
        return True

    def delete(self, obj_id: int) -> bool:
        """Delete a professional and remove its CSV file.

        Parameters
        ----------
        obj_id : int
            ID of the professional to delete.

        Returns
        -------
        bool
            True if deleted, False if the ID is not cached.
        """
        if obj_id not in self.professionals:
            return False

        filename = self.file_map.pop(obj_id, None)
        self.professionals.pop(obj_id, None)

        if filename and os.path.exists(filename):
            os.remove(filename)
        return True

    def select(self, obj_id: int) -> Optional[Professional]:
        """Return a professional from the in-memory cache.

        Parameters
        ----------
        obj_id : int
            The professional ID to look up.

        Returns
        -------
        Professional | None
            The professional, or None if the ID is not cached.
        """
        return self.professionals.get(obj_id)

    def list(self) -> List[Professional]:
        """Return all cached professionals.

        Returns
        -------
        list[Professional]
            The cached professionals, in cache order.
        """
        return list(self.professionals.values())

    def sanitize_filename(self, name: str) -> str:
        """Make a professional name safe for file names.

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
        >>> dao = object.__new__(ProfessionalCsvDAO)
        >>> dao.sanitize_filename(" Ana Maria! ")
        'ana_maria_'
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, professional: Professional) -> str:
        """Return the full path of a professional's CSV file.

        Parameters
        ----------
        professional : Professional
            The professional.

        Returns
        -------
        str
            Path of ``<id>_<sanitized name>_professional.csv`` in the
            professional directory.
        """
        sanitized_name = self.sanitize_filename(professional.name)
        filename = f"{professional.id}_{sanitized_name}_professional.csv"
        return PathConfig.professional(filename)

    def load_all_professionals(self) -> None:
        """Load every professional CSV file into the cache.

        Notes
        -----
        Reads each ``*_professional.csv`` file of the professional
        directory; empty or unreadable files are skipped. Only the first
        row is used. Integer fields that are not plain digits (including
        negative numbers) become 0, and boolean fields are True only for
        ``"true"`` (any case).
        """
        PathConfig.ensure_dirs()
        for file_path in PathConfig.PROFESSIONAL_DIR.glob(
            "*_professional.csv"
        ):
            professional_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if not professional_data:
                continue

            row = professional_data[0]
            professional_kwargs = {}
            for prop in Professional.PROPERTIES:
                if prop in row:
                    if prop == "institutionfacility":
                        institution_id = (
                            int(row[prop]) if row[prop].isdigit() else None
                        )
                        if self.institution_dao and institution_id:
                            professional_kwargs[prop] = (
                                self.institution_dao.select(institution_id)
                            )
                        else:
                            professional_kwargs[prop] = None
                    elif prop in self.int_properties:
                        professional_kwargs[prop] = (
                            int(row[prop]) if row[prop].isdigit() else 0
                        )
                    elif prop in self.bool_properties:
                        professional_kwargs[prop] = row[prop].lower() == "true"
                    else:
                        professional_kwargs[prop] = row[prop]

            professional = Professional(**professional_kwargs)
            self.professionals[professional.id] = professional
            self.file_map[professional.id] = str(file_path)

    def search_professionals(self, query: str = "") -> List[Professional]:
        """Return cached professionals, optionally filtered.

        Parameters
        ----------
        query : str, optional
            Text searched, case-insensitively, in the ID and the name. A
            blank query returns every professional. Default is ``""``.

        Returns
        -------
        list[Professional]
            The matching professionals.
        """
        all_professionals = list(self.professionals.values())

        if not query.strip():
            return all_professionals

        q = query.lower().strip()
        return [
            p
            for p in all_professionals
            if q in str(p.id) or q in p.name.lower()
        ]
