"""Read-only DAO of the Kartea game phases (phase CSV files)."""

from dataclasses import fields

from PySide6.QtCore import QDir, QDirIterator

from ttea.games.kartea.model.karteaphase import KarteaPhase
from ttea.games.kartea.model.karteaphaselevel import KarteaPhaseLevel
from ttea.games.kartea.util.karteapathconfig import KarteaPathConfig
from ttea.util import CSVHandler

from .readonlydao import ReadOnlyDAO


class KarteaPhaseCsvDAO(ReadOnlyDAO):
    """Read-only DAO of KarteaPhase, read from the phase CSV files.

    Each phase is a CSV file (``{phase}.csv``) with one row per level.
    The file in the user's data folder takes priority over the built-in
    resource (see KarteaPathConfig.read_phase_data). This is the only
    place that reads these CSV files: KarteaPhaseLevelCsvDAO queries the
    levels through it.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading CSV content.

    Methods
    -------
    list_phase_ids() -> list[int]
        Ids of the existing phases (user folder + built-in resources).
    load_phase_from_csv(kartea_phase_id) -> KarteaPhase | None
        Read the phase and its levels (each level points to the phase).
    select(obj_id) -> KarteaPhase | None
        Phase by id, with its levels.
    list() -> list[KarteaPhase]
        All phases, ordered by id, with their levels.

    Notes
    -----
    Creating the DAO ensures the KarTEA folders exist. Phases are not
    cached: every call reads the CSV again.
    """

    def __init__(self):
        self.csv_handler = CSVHandler()
        KarteaPathConfig.ensure_kartea_dirs()

    @staticmethod
    def list_phase_ids() -> list[int]:
        """Return the ids of the existing phases.

        Returns
        -------
        list[int]
            Sorted ids, without duplicates, from the CSV files of the
            user's phases folder and of the ``:/phases`` Qt resource.

        Notes
        -----
        Only files whose name (without ``.csv``) is a number count.
        """
        phase_ids: set[int] = set()

        # 1. Ids on disk (user data folder)
        for file in KarteaPathConfig.KARTEA_PHASES_DIR.glob("*.csv"):
            if file.stem.isdigit():
                phase_ids.add(int(file.stem))

        # 2. Ids in the built-in resources (:/phases)
        it = QDirIterator(":/phases", QDir.Files)
        while it.hasNext():
            it.next()
            name = it.fileName().replace(".csv", "")
            if name.isdigit():
                phase_ids.add(int(name))

        return sorted(phase_ids)

    def load_phase_from_csv(self, kartea_phase_id: int) -> KarteaPhase | None:
        """Read a phase and its levels.

        Parameters
        ----------
        kartea_phase_id : int
            Id of the phase (name of its CSV file).

        Returns
        -------
        KarteaPhase | None
            The phase with ``level_list`` filled, or None if the file
            does not exist, is empty or has no valid level.

        Notes
        -----
        - Rows whose ``phase`` column differs from ``kartea_phase_id``
          are skipped, as are rows without an ``id``.
        - ``obj_type`` is parsed from space-separated numbers;
          non-numeric tokens are ignored.
        - Columns annotated as int or float in KarteaPhaseLevel are
          converted; the others keep the text.
        """
        # KarteaPathConfig resolves the priority: disk > resource
        content = KarteaPathConfig.read_phase_data(kartea_phase_id)
        if not content:
            return None

        phase_data = self.csv_handler.read_csv(content=content, as_dict=True)
        if not phase_data:
            return None

        phase = KarteaPhase(id=kartea_phase_id, level_list=[])
        level_fields = {f.name: f.type for f in fields(KarteaPhaseLevel)}

        for row in phase_data:
            if "phase" in row and int(row["phase"]) != kartea_phase_id:
                continue

            level_kwargs = {}
            for prop in KarteaPhaseLevel.PROPERTIES:
                if prop == "phase":
                    level_kwargs[prop] = phase
                elif prop == "obj_type" and prop in row:
                    level_kwargs[prop] = [
                        int(x)
                        for x in row.get(prop, "").strip().split()
                        if x.strip().isdigit()
                    ]
                elif prop in row:
                    t = level_fields.get(prop)
                    level_kwargs[prop] = (
                        t(row[prop]) if t in (int, float) else row[prop]
                    )

            if "id" in level_kwargs:
                phase.level_list.append(KarteaPhaseLevel(**level_kwargs))

        return phase if phase.level_list else None

    def select(self, obj_id: int) -> KarteaPhase | None:
        """Return the phase with the given id, with its levels.

        Parameters
        ----------
        obj_id : int
            Id of the phase.

        Returns
        -------
        KarteaPhase | None
            The phase read from the CSV, or None if it does not exist.
        """
        return self.load_phase_from_csv(obj_id)

    def list(self) -> list[KarteaPhase]:
        """Return all existing phases, ordered by id.

        Returns
        -------
        list[KarteaPhase]
            Phases with their levels; phases without levels are left
            out.
        """
        phases = []
        for phase_id in self.list_phase_ids():
            phase = self.load_phase_from_csv(phase_id)
            if phase:
                phases.append(phase)
        return phases
