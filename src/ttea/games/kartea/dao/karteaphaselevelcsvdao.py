"""Read-only DAO of the levels of the Kartea game phases."""

from ttea.games.kartea.model.karteaphaselevel import KarteaPhaseLevel

from .karteaphasecsvdao import KarteaPhaseCsvDAO
from .readonlydao import ReadOnlyDAO


class KarteaPhaseLevelCsvDAO(ReadOnlyDAO):
    """Read-only DAO of KarteaPhaseLevel.

    The levels come from KarteaPhaseCsvDAO (reading the phase CSV files
    happens only there). Each level points to its phase, which holds the
    full list of levels.

    Parameters
    ----------
    phase_dao : KarteaPhaseCsvDAO | None, optional
        Phase DAO to share. If None, a new one is created.

    Attributes
    ----------
    phase_dao : KarteaPhaseCsvDAO
        DAO of the phases (shared, if given).
    """

    def __init__(self, phase_dao: KarteaPhaseCsvDAO | None = None):
        self.phase_dao = phase_dao or KarteaPhaseCsvDAO()

    def load_levels_from_csv(self, phase_id: int) -> list[KarteaPhaseLevel]:
        """Return the levels of a phase in the CSV order.

        Parameters
        ----------
        phase_id : int
            Id of the phase.

        Returns
        -------
        list[KarteaPhaseLevel]
            The levels, or an empty list if the phase does not exist.
        """
        phase = self.phase_dao.load_phase_from_csv(phase_id)
        return phase.level_list if phase else []

    def select(self, phase_id: int, level_id: int) -> KarteaPhaseLevel | None:
        """Return a level by phase and level id.

        Parameters
        ----------
        phase_id : int
            Id of the phase.
        level_id : int
            Id of the level within the phase.

        Returns
        -------
        KarteaPhaseLevel | None
            The level, or None if not found.

        Notes
        -----
        Unlike the base DAO, ``select`` takes two keys, since level ids
        repeat across phases.
        """
        for level in self.load_levels_from_csv(phase_id):
            if level.id == level_id:
                return level
        return None

    def list(self) -> list[KarteaPhaseLevel]:
        """Return the levels of all phases, ordered by phase.

        Returns
        -------
        list[KarteaPhaseLevel]
            All levels.
        """
        return [
            level
            for phase in self.phase_dao.list()
            for level in phase.level_list
        ]
