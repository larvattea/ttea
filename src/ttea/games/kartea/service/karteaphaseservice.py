"""Service of the KarTEA phases and levels.

Attributes
----------
LEVEL_ACTION_NEXT, LEVEL_ACTION_PREVIOUS, LEVEL_ACTION_RESTART : str
    Level actions accepted by ``KarteaPhaseService.change_level``
    ("next", "prev" and "rest").
SPEED_BY_LEVEL : dict[int, int]
    Track speed range by level: levels 1-2 slow (1), 3-4 medium (2).
DEFAULT_SPEED : int
    Speed range of the other levels (5 onwards): fast (3).
DEFAULT_LEVEL_INTERVAL : float
    Interval (s) between objects when the phase/level does not exist
    in the CSV files.
"""

from ttea.games.kartea.dao import KarteaPhaseCsvDAO
from ttea.games.kartea.model import KarteaPhase, KarteaPhaseLevel, LevelRules

LEVEL_ACTION_NEXT = "next"
LEVEL_ACTION_PREVIOUS = "prev"
LEVEL_ACTION_RESTART = "rest"

# Hardcoded because the phase CSV files have no speed column.
SPEED_BY_LEVEL = {1: 1, 2: 1, 3: 2, 4: 2}
DEFAULT_SPEED = 3

DEFAULT_LEVEL_INTERVAL = 8.0


class KarteaPhaseService:
    """Service (MVCS) of the KarTEA phases and levels.

    Business rules of the phases, read from the CSV files
    (resources/phases): which phases and levels exist, the progression
    between them (advance, regress) and the rules of each level
    (interval, amount and type of objects, speed range).

    Parameters
    ----------
    dao : KarteaPhaseCsvDAO | None, optional
        DAO of the phases. Created if None. Kept private.

    Notes
    -----
    The CSV files are read once, on first use, and kept in cache
    (phases in order, the sorted level ids of each phase, and each
    KarteaPhaseLevel indexed by the (phase, level) pair).

    Examples
    --------
    >>> from types import SimpleNamespace as NS
    >>> phases = [
    ...     NS(id=1, level_list=[NS(id=1), NS(id=2)]),
    ...     NS(id=2, level_list=[NS(id=1)]),
    ... ]
    >>> service = KarteaPhaseService(dao=NS(list=lambda: phases))
    >>> service.next_level(1, 1)
    (1, 2)
    >>> service.next_level(1, 2)
    (2, 1)
    >>> service.previous_level(2, 1)
    (2, 1)
    """

    def __init__(self, dao: KarteaPhaseCsvDAO | None = None):
        self._dao = dao or KarteaPhaseCsvDAO()
        self._phases: dict[int, KarteaPhase] | None = None
        self._progression: dict[int, list[int]] | None = None
        self._levels: dict[tuple[int, int], KarteaPhaseLevel] | None = None

    def _load(self) -> None:
        """Read the phases from the CSV files and fill the caches."""
        self._phases = {}
        self._progression = {}
        self._levels = {}
        for phase in self._dao.list():
            self._phases[phase.id] = phase
            if not phase.level_list:
                continue
            self._progression[phase.id] = sorted(
                level.id for level in phase.level_list
            )
            for level in phase.level_list:
                self._levels[(phase.id, level.id)] = level

    def _ensure_loaded(self) -> None:
        """Load the phases on first use."""
        if self._phases is None:
            self._load()

    # ======================
    # Queries
    # ======================
    def get_all_phases(self) -> list[KarteaPhase]:
        """Return the available phases, ordered by id.

        Returns
        -------
        list[KarteaPhase]
            All phases read from the CSV files.
        """
        self._ensure_loaded()
        return [self._phases[pid] for pid in sorted(self._phases)]

    def get_phase(self, phase_id: int) -> KarteaPhase | None:
        """Return the phase with the given id.

        Parameters
        ----------
        phase_id : int
            Id of the phase.

        Returns
        -------
        KarteaPhase | None
            The phase, or None if it does not exist.
        """
        self._ensure_loaded()
        return self._phases.get(phase_id)

    def get_levels_for_phase(
        self, phase: int | KarteaPhase | None
    ) -> list[KarteaPhaseLevel]:
        """Return the levels of a phase, ordered by level id.

        Parameters
        ----------
        phase : int | KarteaPhase | None
            Phase id or object.

        Returns
        -------
        list[KarteaPhaseLevel]
            The levels, or an empty list if the phase is None, does not
            exist or has no levels.
        """
        if phase is None:
            return []
        phase_id = phase if isinstance(phase, int) else phase.id
        self._ensure_loaded()
        return [
            self._levels[(phase_id, level_id)]
            for level_id in self._progression.get(phase_id, [])
        ]

    def get_level(
        self, phase_id: int, level_id: int
    ) -> KarteaPhaseLevel | None:
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
            The level, or None if it does not exist.
        """
        self._ensure_loaded()
        return self._levels.get((phase_id, level_id))

    # ======================
    # Progression
    # ======================
    def next_level(self, phase_id: int, level_id: int) -> tuple[int, int]:
        """Return the next phase/level.

        Parameters
        ----------
        phase_id : int
            Current phase.
        level_id : int
            Current level.

        Returns
        -------
        tuple[int, int]
            The (phase, level) to play next.

        Notes
        -----
        Advances one level within the phase; after the last level of the
        phase, moves to the first level of the next phase. On the last
        level of the last phase, stays. Uses the actual number of phases
        and levels in the CSV files.
        """
        self._ensure_loaded()
        levels = self._progression.get(phase_id, [])
        later = [level for level in levels if level > level_id]
        if later:
            return phase_id, later[0]
        for next_phase in sorted(self._progression):
            if next_phase > phase_id:
                return next_phase, self._progression[next_phase][0]
        return phase_id, level_id

    def previous_level(self, phase_id: int, level_id: int) -> tuple[int, int]:
        """Return the previous phase/level, one level back in the phase.

        Parameters
        ----------
        phase_id : int
            Current phase.
        level_id : int
            Current level.

        Returns
        -------
        tuple[int, int]
            The (phase, level) to play next.

        Notes
        -----
        On the first level of the phase, stays (does not go back a
        phase).
        """
        self._ensure_loaded()
        levels = self._progression.get(phase_id, [])
        earlier = [level for level in levels if level < level_id]
        if earlier:
            return phase_id, earlier[-1]
        return phase_id, level_id

    def change_level(
        self, phase_id: int, level_id: int, action: str
    ) -> tuple[int, int]:
        """Apply a level action ("next", "prev" or "rest").

        Parameters
        ----------
        phase_id : int
            Current phase.
        level_id : int
            Current level.
        action : str
            LEVEL_ACTION_NEXT, LEVEL_ACTION_PREVIOUS or
            LEVEL_ACTION_RESTART.

        Returns
        -------
        tuple[int, int]
            The resulting (phase, level). "rest" (restart) and any
            unknown action keep the current phase and level.
        """
        if action == LEVEL_ACTION_NEXT:
            return self.next_level(phase_id, level_id)
        if action == LEVEL_ACTION_PREVIOUS:
            return self.previous_level(phase_id, level_id)
        return phase_id, level_id

    # ======================
    # Level rules
    # ======================
    @staticmethod
    def speed_for_level(level_id: int) -> int:
        """Return the speed range (1, 2 or 3) of a level.

        Parameters
        ----------
        level_id : int
            Id of the level.

        Returns
        -------
        int
            1 for levels 1-2, 2 for levels 3-4 and 3 (DEFAULT_SPEED) for
            the others. The phase CSV files have no speed column.

        Examples
        --------
        >>> KarteaPhaseService.speed_for_level(3)
        2
        >>> KarteaPhaseService.speed_for_level(7)
        3
        """
        return SPEED_BY_LEVEL.get(level_id, DEFAULT_SPEED)

    def get_level_rules(self, phase_id: int, level_id: int) -> LevelRules:
        """Return the rules of a level, read from the phase CSV file.

        Parameters
        ----------
        phase_id : int
            Id of the phase.
        level_id : int
            Id of the level.

        Returns
        -------
        LevelRules
            ``interval`` (s between objects), ``num_obj`` (maximum
            number of objects) and ``obj_types`` (0 target, 1 obstacle,
            in order) from the CSV, plus the speed range of the level.

        Notes
        -----
        If the phase/level does not exist, default rules are returned:
        interval DEFAULT_LEVEL_INTERVAL, no object limit and random
        types.
        """
        level = self.get_level(phase_id, level_id)
        speed = self.speed_for_level(level_id)
        if level is None:
            return LevelRules(
                phase=phase_id,
                level=level_id,
                interval=DEFAULT_LEVEL_INTERVAL,
                num_obj=0,
                obj_types=[],
                speed=speed,
            )
        return LevelRules(
            phase=phase_id,
            level=level_id,
            interval=float(level.interval),
            num_obj=int(level.num_obj),
            obj_types=list(level.obj_type or []),
            speed=speed,
        )
