"""Model of a level within a Kartea game phase."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .reflexivemodel import ReflexiveModel, initialize_reflexive

if TYPE_CHECKING:
    from ttea.games.kartea.model.karteaphase import KarteaPhase


@initialize_reflexive
@dataclass
class KarteaPhaseLevel(ReflexiveModel):
    """Summary model for Kartea game phase level data.

    Attributes
    ----------
    id : int
        Unique identifier for the level.
    phase : KarteaPhase
        The phase associated with this level.
    interval : float
        Time interval between objects (in seconds).
    num_obj : int
        Number of objects in the level.
    obj_type : list[int]
        Type of each object, in order (0 target, 1 obstacle), parsed
        from the space-separated ``obj_type`` column of the phase CSV.
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the class, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field (``dataclasses.MISSING`` when
        the field has none), filled by ``initialize_reflexive``.
    REF_PROPERTIES : tuple[str, ...], class attribute
        Fields written as the referenced object's ``id`` by
        ``get_data``: ``("phase",)``.

    Methods
    -------
    set_data(data)
        Update level data from a dictionary.
    get_data()
        Return level data as a list with one dictionary.

    See Also
    --------
    KarteaPhase : Phase that owns the level.
    LevelRules : Rules of a level used while the game is running.

    Examples
    --------
    >>> from ttea.games.kartea.model.karteaphase import KarteaPhase
    >>> phase = KarteaPhase(id=1, level_list=[])
    >>> level = KarteaPhaseLevel(
    ...     id=1, phase=phase, interval=1.5, num_obj=10,
    ...     obj_type=[1, 2, 3],
    ... )
    >>> level.get_data()  # doctest: +NORMALIZE_WHITESPACE
    [{'id': 1, 'phase': 1, 'interval': 1.5, 'num_obj': 10,
      'obj_type': [1, 2, 3]}]
    """

    id: int
    phase: "KarteaPhase"
    interval: float
    num_obj: int
    obj_type: list[int]
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
    REF_PROPERTIES = ("phase",)
