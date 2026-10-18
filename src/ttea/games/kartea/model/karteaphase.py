"""Model of a Kartea game phase."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .reflexivemodel import ReflexiveModel, initialize_reflexive

if TYPE_CHECKING:
    from ttea.games.kartea.model.karteaphaselevel import KarteaPhaseLevel


@initialize_reflexive
@dataclass
class KarteaPhase(ReflexiveModel):
    """Summary model for Kartea game phase data.

    Attributes
    ----------
    id : int
        Unique identifier for the phase.
    level_list : list[KarteaPhaseLevel]
        Levels of the phase, in the order of the phase CSV file.
    PROPERTIES : ClassVar[list[str]], class attribute
        Field names of the class, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : ClassVar[list], class attribute
        Default value of each init field (``dataclasses.MISSING`` when
        the field has none), filled by ``initialize_reflexive``.

    Methods
    -------
    set_data(data)
        Update phase data from a dictionary.
    get_data()
        Return phase data as a list with one dictionary.

    See Also
    --------
    KarteaPhaseLevel : Level of a phase.
    ReflexiveModel : Provides ``set_data`` and ``get_data``.

    Notes
    -----
    ``KarteaPhaseCsvDAO`` creates the phase with an empty
    ``level_list`` and appends one ``KarteaPhaseLevel`` per CSV row.

    Examples
    --------
    >>> phase = KarteaPhase(id=1, level_list=[])
    >>> phase.get_data()
    [{'id': 1, 'level_list': []}]
    """

    id: int
    level_list: list["KarteaPhaseLevel"]
    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []
