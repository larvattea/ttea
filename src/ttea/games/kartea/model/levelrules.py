"""Rules of a game level, read from the phase CSV files.

The module constants ``OBJ_TYPE_TARGET`` (0) and ``OBJ_TYPE_OBSTACLE``
(1) are the object types used in ``obj_type``.
"""

from dataclasses import dataclass, field

OBJ_TYPE_TARGET = 0
OBJ_TYPE_OBSTACLE = 1


@dataclass(frozen=True)
class LevelRules:
    """What defines a level: pace, amount and type of the objects.

    Attributes
    ----------
    phase : int
        Phase the rules refer to.
    level : int
        Level the rules refer to.
    interval : float
        Interval (s) between objects (``interval`` column of the CSV).
    num_obj : int
        Maximum number of objects in the level (``num_obj`` column);
        0 means no limit.
    obj_types : list[int]
        Type of each object, in order: 0 target, 1 obstacle
        (``obj_type`` column). Objects beyond the list get a random
        type. Defaults to an empty list.
    speed : int
        Speed range of the track (1, 2 or 3), used with
        GameSettings.OBJECT_ARRIVAL_TIME (times configured per player:
        object_arrival_time_1/2/3). Defaults to 1.
    """

    phase: int
    level: int
    interval: float
    num_obj: int
    obj_types: list[int] = field(default_factory=list)
    speed: int = 1

    def allows_more(self, spawned: int) -> bool:
        """Check whether another object still fits in the level.

        Parameters
        ----------
        spawned : int
            Number of objects already created in the level.

        Returns
        -------
        bool
            True if ``num_obj`` is 0 or less (no limit) or if
            ``spawned`` is below ``num_obj``.

        Examples
        --------
        >>> rules = LevelRules(1, 1, interval=1.5, num_obj=2)
        >>> rules.allows_more(1)
        True
        >>> rules.allows_more(2)
        False
        """
        return self.num_obj <= 0 or spawned < self.num_obj

    def object_type(self, index: int) -> int | None:
        """Return the type of the object at position ``index``.

        Parameters
        ----------
        index : int
            Zero-based order of the object in the level.

        Returns
        -------
        int | None
            The type from ``obj_types`` (0 target, 1 obstacle), or None
            when ``index`` is outside the list (the caller then picks
            a random type).

        Examples
        --------
        >>> rules = LevelRules(1, 1, 1.5, 0, obj_types=[0, 1])
        >>> rules.object_type(1)
        1
        >>> rules.object_type(5) is None
        True
        """
        if 0 <= index < len(self.obj_types):
            return self.obj_types[index]
        return None
