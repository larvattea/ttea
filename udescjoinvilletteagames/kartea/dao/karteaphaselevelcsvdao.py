import os
from dataclasses import fields
from typing import Any, List, Optional

from udescjoinvilletteadao import DAO
from udescjoinvilletteagames.kartea.model.karteaphase import KarteaPhase
from udescjoinvilletteagames.kartea.model.karteaphaselevel import (
    KarteaPhaseLevel,
)
from udescjoinvilletteagames.kartea.util.karteapathconfig import (
    KarteaPathConfig,
)
from udescjoinvilletteautil import CSVHandler


class KarteaPhaseLevelCsvDAO(DAO):
    """Data Access Object for KarteaPhaseLevel, handling query operations
    by reading CSV files physically.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV files.

    Methods
    -------
    __init__()
        Initializes the DAO with a CSV handler.
    load_levels_from_csv(phase_id: int) -> List[KarteaPhaseLevel]
        Loads all KarteaPhaseLevel for a given phase ID from a CSV file.
    select(obj_id: int) -> Optional[KarteaPhaseLevel]
        Retrieves a single KarteaPhaseLevel by ID.
    list() -> List[KarteaPhaseLevel]
        Retrieves a list of all KarteaPhaseLevel across all phases.
    insert(obj: object) -> Optional[Any]
        Placeholder for insert operation (not implemented).
    update(obj: object) -> Optional[Any]
        Placeholder for update operation (not implemented).
    delete(obj_id: int) -> Optional[Any]
        Placeholder for delete operation (not implemented).
    """

    def __init__(self):
        """Initialize the KarteaPhaseLevelDAO with a CSV handler.

        Returns
        -------
        None

        Notes
        -----
        Creates necessary directories using KarteaPathConfig.
        """
        self.csv_handler = CSVHandler()
        KarteaPathConfig.ensure_kartea_dirs()

    def load_levels_from_csv(self, phase_id: int) -> List[KarteaPhaseLevel]:
        """Load all KarteaPhaseLevel for a given phase ID from a CSV file.

        Parameters
        ----------
        phase_id : int
            The ID of the phase to load levels from.

        Returns
        -------
        List[KarteaPhaseLevel]
            A list of KarteaPhaseLevel objects, or empty list if not found.

        Notes
        -----
        Reads the CSV file named '{phase_id}.csv' from kartea_phases_dir.
        Uses KarteaPhaseLevel.PROPERTIES to map CSV columns to fields.
        Validates that the 'phase' column matches phase_id.
        Parses 'obj_type' as a list of integers from a space-separated string.
        """
        file_path = KarteaPathConfig.KARTEA_PHASES_DIR / f"{phase_id}.csv"
        if not os.path.exists(file_path):
            return []

        phase_data = self.csv_handler.read_csv(str(file_path), as_dict=True)
        if not phase_data:
            return []

        levels = []
        temp_phase = KarteaPhase(id=phase_id, level_list=[])

        # Infer field types for conversion
        level_fields = {f.name: f.type for f in fields(KarteaPhaseLevel)}

        for row in phase_data:
            # Validate phase ID in CSV matches file name
            if "phase" in row and int(row["phase"]) != phase_id:
                continue  # Skip rows with mismatched phase ID

            # Build kwargs dynamically from PROPERTIES
            level_kwargs = {}
            for prop in KarteaPhaseLevel.PROPERTIES:
                if prop == "phase":
                    level_kwargs[prop] = temp_phase
                elif prop == "obj_type" and prop in row:
                    level_kwargs[prop] = [
                        int(x)
                        for x in row.get(prop, "").strip().split()
                        if x.strip().isdigit()
                    ]
                elif prop in row:
                    # Convert based on field type
                    if level_fields[prop] == int:
                        level_kwargs[prop] = int(row[prop])
                    elif level_fields[prop] == float:
                        level_kwargs[prop] = float(row[prop])
                    else:
                        level_kwargs[prop] = row[prop]

            # Only create level if required fields are present
            if "id" in level_kwargs:
                level = KarteaPhaseLevel(**level_kwargs)
                levels.append(level)

        return levels

    def select(self, obj_id: int) -> Optional[KarteaPhaseLevel]:
        """Retrieve a single KarteaPhaseLevel by ID by reading all
        phase CSV files.

        Parameters
        ----------
        obj_id : int
            The ID of the level to retrieve.

        Returns
        -------
        Optional[KarteaPhaseLevel]
            The KarteaPhaseLevel object if found, None otherwise.

        Notes
        -----
        Iterates through all phase CSV files to find the level with
        the given ID.
        Sets the phase reference for the level to include all levels
        of the phase.
        """
        KarteaPathConfig.ensure_kartea_dirs()
        phase_files = sorted(
            KarteaPathConfig.KARTEA_PHASES_DIR.glob("*.csv"),
            key=lambda x: int(x.stem),
        )
        for file_path in phase_files:
            phase_number = int(file_path.stem)
            levels = self.load_levels_from_csv(phase_number)
            for level in levels:
                if level.id == obj_id:
                    phase = KarteaPhase(id=phase_number, level_list=levels)
                    level.phase = phase
                    return level
        return None

    def list(self) -> List[KarteaPhaseLevel]:
        """Retrieve a list of all KarteaPhaseLevel across all phases.

        Returns
        -------
        List[KarteaPhaseLevel]
            A list of all KarteaPhaseLevel objects found in CSV files.

        Notes
        -----
        Iterates through all phase CSV files, loads levels, and
        sets phase references.
        """
        KarteaPathConfig.create_directories()
        all_levels = []
        phase_files = sorted(
            KarteaPathConfig.KARTEA_PHASES_DIR.glob("*.csv"),
            key=lambda x: int(x.stem),
        )
        for file_path in phase_files:
            phase_number = int(file_path.stem)
            levels = self.load_levels_from_csv(phase_number)
            if levels:
                phase = KarteaPhase(id=phase_number, level_list=levels)
                for level in levels:
                    level.phase = phase
                    all_levels.append(level)
        return all_levels

    def insert(self, obj: object) -> Optional[Any]:
        """Placeholder for insert operation.

        Parameters
        ----------
        obj : object
            The object to insert.

        Returns
        -------
        Optional[Any]
            Not implemented.

        Raises
        ------
        NotImplementedError
            Always raised as the method is not implemented.
        """
        raise NotImplementedError

    def update(self, obj: object) -> Optional[Any]:
        """Placeholder for update operation.

        Parameters
        ----------
        obj : object
            The object to update.

        Returns
        -------
        Optional[Any]
            Not implemented.

        Raises
        ------
        NotImplementedError
            Always raised as the method is not implemented.
        """
        raise NotImplementedError

    def delete(self, obj_id: int) -> Optional[Any]:
        """Placeholder for delete operation.

        Parameters
        ----------
        obj_id : int
            The ID of the object to delete.

        Returns
        -------
        Optional[Any]
            Not implemented.

        Raises
        ------
        NotImplementedError
            Always raised as the method is not implemented.
        """
        raise NotImplementedError
