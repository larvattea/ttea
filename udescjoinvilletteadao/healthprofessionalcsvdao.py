import os
import re
from dataclasses import fields
from typing import TYPE_CHECKING, Dict, List, Optional

import portalocker

# Local module import
from udescjoinvilletteadao import DAO
from udescjoinvilletteamodel import HealthProfessional
from udescjoinvilletteautil import CSVHandler, PathConfig

if TYPE_CHECKING:
    from udescjoinvilletteadao import InstitutionFacilityCsvDAO


class HealthProfessionalCsvDAO(DAO[HealthProfessional]):
    """Specialized DAO for healthprofessional entities using CSV files
    with in-memory cache.
    """

    def __init__(
        self, institution_dao: Optional["InstitutionFacilityCsvDAO"] = None
    ) -> None:
        """Initialize the DAO and load all healthprofessionals
        from CSV files."""
        from udescjoinvilletteadao import InstitutionFacilityCsvDAO

        self.csv_handler = CSVHandler()
        self.healthprofessionals: Dict[int, HealthProfessional] = {}
        self.file_map: Dict[int, str] = {}
        self.int_properties = [
            f.name for f in fields(HealthProfessional) if f.type == int
        ]
        self.bool_properties = [
            f.name for f in fields(HealthProfessional) if f.type == bool
        ]
        self.institution_dao = institution_dao or InstitutionFacilityCsvDAO()
        self.load_all_healthprofessionals()

    def generate_next_id(self) -> int:
        """Generate the next available InstitutionFacility ID.

        Returns
        -------
        int
            The next unused ID (1 if no InstitutionFacility exist).
        """
        if not self.healthprofessionals:
            return 1
        return max(self.healthprofessionals.keys()) + 1

    def write_with_lock(
        self, filepath: str, data: List[Dict], headers: List[str]
    ):
        """Write data to a CSV file with exclusive file locking.

        Parameters
        ----------
        filepath : str
            Full path to the target CSV file.
        data : List[Dict]
            List of dictionaries representing rows to write.
        headers : List[str]
            Ordered list of column names.
        """
        PathConfig.ensure_user_dirs()
        with portalocker.Lock(filepath, mode="w", timeout=10) as f:
            self.csv_handler.write_csv(f, data, headers)

    def insert(self, obj: HealthProfessional) -> int:
        """Insert a new healthprofessional into persistent storage.

        Parameters
        ----------
        obj : InstitutionFacility
            The InstitutionFacility instance to persist.

        Returns
        -------
        int
            The assigned healthprofessional ID on success,
            0 on failure (invalid healthprofessional or ID already exists).
        """
        if not obj.is_valid():
            return 0

        # Generate ID if not set
        if obj.id <= 0:
            obj.id = self.generate_next_id()

        if obj.id in self.healthprofessionals:
            return 0

        self.healthprofessionals[obj.id] = obj
        filename = self.get_filename(obj)
        self.file_map[obj.id] = filename
        self.write_with_lock(
            filename, obj.get_data(), HealthProfessional.PROPERTIES
        )
        return obj.id

    def update(self, obj: HealthProfessional) -> bool:
        """Update an existing healthprofessional in persistent storage.

        Renames the file if the healthprofessional's name changed.

        Parameters
        ----------
        obj : HealthProfessional
            The healthprofessional with updated values.

        Returns
        -------
        bool
            True if updated successfully, False otherwise.
        """
        if not obj.is_valid() or obj.id not in self.healthprofessionals:
            return False

        old_filename = self.file_map.get(obj.id)
        new_filename = self.get_filename(obj)

        if old_filename != new_filename and os.path.exists(old_filename):
            os.rename(old_filename, new_filename)

        self.healthprofessionals[obj.id] = obj
        self.file_map[obj.id] = new_filename
        self.write_with_lock(
            new_filename, obj.get_data(), HealthProfessional.PROPERTIES
        )
        return True

    def delete(self, obj_id: int) -> bool:
        """Delete a healthprofessional and remove its CSV file.

        Parameters
        ----------
        obj_id : int
            ID of the healthprofessional to delete.

        Returns
        -------
        bool
            True if deleted, False if the healthprofessional was not found.
        """
        if obj_id not in self.healthprofessionals:
            return False

        filename = self.file_map.pop(obj_id, None)
        self.healthprofessionals.pop(obj_id, None)

        if filename and os.path.exists(filename):
            os.remove(filename)
        return True

    def select(self, obj_id: int) -> Optional[HealthProfessional]:
        """Retrieve a healthprofessional by ID from the in-memory cache.

        Parameters
        ----------
        obj_id : int
            The healthprofessional ID to look up.

        Returns
        -------
        Optional[HealthProfessional]
            The HealthProfessional instance if found, None otherwise.
        """
        return self.healthprofessionals.get(obj_id)

    def list(self) -> List[HealthProfessional]:
        """Return all loaded healthprofessionals.

        Returns
        -------
        List[InstitutionFacility]
            A list of all InstitutionFacility instances currently in memory.
        """
        return list(self.healthprofessionals.values())

    def sanitize_filename(self, name: str) -> str:
        """Sanitize a healthprofessional name for safe use in filenames.

        Parameters
        ----------
        name : str
            Original healthprofessional name.

        Returns
        -------
        str
            Sanitized name (lowercase, non-alphanumeric replaced by '_').
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, healthprofessional: HealthProfessional) -> str:
        """Generate the full path for a healthprofessional's CSV file.

        Parameters
        ----------
        healthprofessional : HealthProfessional
            The healthprofessional object.

        Returns
        -------
        str
            Complete file path using pattern:
            <id>_<sanitized_name>_healthprofessional.csv
        """
        sanitized_name = self.sanitize_filename(healthprofessional.name)
        filename = (
            f"{healthprofessional.id}_{sanitized_name}_healthprofessional.csv"
        )
        return PathConfig.healthprofessional(filename)

    def load_all_healthprofessionals(self) -> None:
        """Load every healthprofessional CSV file from disk into memory.

        Scans the healthprofessionals directory, parses each
        matching CSV file, converts data types appropriately,
        and populates the cache.
        """
        PathConfig.ensure_user_dirs()
        for file_path in PathConfig.HEALTHPROFESSIONAL_DIR.glob(
            "*_healthprofessional.csv"
        ):
            healthprofessional_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if not healthprofessional_data:
                continue

            row = healthprofessional_data[0]
            # Build healthprofessional kwargs with type conversions
            healthprofessional_kwargs = {}
            for prop in HealthProfessional.PROPERTIES:
                if prop in row:
                    # Special handling for institutionfacility to load the full object
                    if prop == "institutionfacility":
                        institution_id = (
                            int(row[prop]) if row[prop].isdigit() else None
                        )
                        if self.institution_dao and institution_id:
                            # Busca o objeto completo da instituição pelo ID
                            healthprofessional_kwargs[prop] = (
                                self.institution_dao.select(institution_id)
                            )
                        else:
                            healthprofessional_kwargs[prop] = None
                    elif prop in self.int_properties:
                        healthprofessional_kwargs[prop] = (
                            int(row[prop]) if row[prop].isdigit() else 0
                        )
                    elif prop in self.bool_properties:
                        healthprofessional_kwargs[prop] = (
                            row[prop].lower() == "true"
                        )
                    else:
                        healthprofessional_kwargs[prop] = row[prop]

            healthprofessional = HealthProfessional(
                **healthprofessional_kwargs
            )
            self.healthprofessionals[healthprofessional.id] = (
                healthprofessional
            )
            self.file_map[healthprofessional.id] = str(file_path)

    def search_healthprofessionals(
        self, query: str = ""
    ) -> List[HealthProfessional]:
        """Retorna a lista de instituições, opcionalmente filtrada."""
        all_healthprofessionals = list(self.healthprofessionals.values())

        if not query.strip():
            return all_healthprofessionals

        q = query.lower().strip()
        return [
            p
            for p in all_healthprofessionals
            if q in str(p.id) or q in p.name.lower()
        ]
