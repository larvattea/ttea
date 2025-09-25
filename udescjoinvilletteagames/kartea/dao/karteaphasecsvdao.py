import os
from dataclasses import fields
from typing import Any, List, Optional

from udescjoinvilletteadao import DAO
from udescjoinvilletteagames.kartea.model.karteaphase import KarteaPhase
from udescjoinvilletteagames.kartea.model.karteaphaselevel import \
    KarteaPhaseLevel
from udescjoinvilletteagames.kartea.util.karteapathconfig import \
    KarteaPathConfig
from udescjoinvilletteautil import CSVHandler


class KarteaPhaseCsvDAO(DAO):
    """Data Access Object for KarteaPhase, handling query operations
    by reading CSV files physically.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV files.

    Methods
    -------
    __init__()
        Initializes the DAO with a CSV handler.
    load_phase_from_csv(kartea_phase_id: int) -> Optional[KarteaPhase]
        Loads a KarteaPhase and its levels from a CSV file using PROPERTIES.
    select(obj_id: int) -> Optional[KarteaPhase]
        Retrieves a single KarteaPhase by ID, including its levels.
    list() -> List[KarteaPhase]
        Retrieves a list of all KarteaPhases, each including its levels.
    insert(obj: object) -> Optional[Any]
        Placeholder for insert operation (not implemented).
    update(obj: object) -> Optional[Any]
        Placeholder for update operation (not implemented).
    delete(obj_id: int) -> Optional[Any]
        Placeholder for delete operation (not implemented).
    """

    def __init__(self):
        """Initialize the KarteaPhaseDAO with a CSV handler.

        Returns
        -------
        None

        Notes
        -----
        Creates necessary directories using KarteaPathConfig.
        """
        self.csv_handler = CSVHandler()
        KarteaPathConfig.create_directories()

    def load_phase_from_csv(
        self, kartea_phase_id: int
    ) -> Optional[KarteaPhase]:
        """Load a KarteaPhase and its levels from a CSV file using PROPERTIES.

        Parameters
        ----------
        kartea_phase_id : int
            The ID of the phase to load.

        Returns
        -------
        Optional[KarteaPhase]
            The KarteaPhase object with its levels, or None if not found.

        Notes
        -----
        Reads the CSV file named '{kartea_phase_id}.csv'
        from kartea_phases_dir.
        Uses KarteaPhaseLevel.PROPERTIES to map CSV columns to fields.
        Validates that the 'phase' column matches kartea_phase_id.
        Parses 'obj_type' as a list of integers from a space-separated string.
        Sets the phase reference for each level after creation.
        """
        file_path = (
            KarteaPathConfig.kartea_phases_dir / f"{kartea_phase_id}.csv"
        )
        if not os.path.exists(file_path):
            return None

        phase_data = self.csv_handler.read_csv(str(file_path), as_dict=True)
        if not phase_data:
            return None

        levels = []
        temp_phase = KarteaPhase(id=kartea_phase_id, level_list=[])

        # Infer field types for conversion
        level_fields = {f.name: f.type for f in fields(KarteaPhaseLevel)}

        for row in phase_data:
            # Validate phase ID in CSV matches file name
            if "phase" in row and int(row["phase"]) != kartea_phase_id:
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

        if not levels:
            return None

        # Create final phase and set level references
        phase = KarteaPhase(id=kartea_phase_id, level_list=levels)
        for level in levels:
            level.phase = phase

        return phase

    def select(self, obj_id: int) -> Optional[KarteaPhase]:
        """Retrieve a single KarteaPhase by ID, including its levels.

        Parameters
        ----------
        obj_id : int
            The ID of the phase to retrieve.

        Returns
        -------
        Optional[KarteaPhase]
            The KarteaPhase object if found, None otherwise.

        Notes
        -----
        Calls _load_phase_from_csv to read the CSV file.
        """
        return self.load_phase_from_csv(obj_id)

    def list(self) -> List[KarteaPhase]:
        """Retrieve a list of all KarteaPhases, each including its levels.

        Returns
        -------
        List[KarteaPhase]
            A list of all KarteaPhase objects found in CSV files.

        Notes
        -----
        Iterates through all '*.csv' files in kartea_phases_dir, sorted by
        phase ID. Calls _load_phase_from_csv for each file.
        """
        KarteaPathConfig.create_directories()
        phases = []
        phase_files = sorted(
            KarteaPathConfig.kartea_phases_dir.glob("*.csv"),
            key=lambda x: int(x.stem),
        )
        for file_path in phase_files:
            phase_number = int(file_path.stem)
            phase = self.load_phase_from_csv(phase_number)
            if phase:
                phases.append(phase)
        return phases

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
