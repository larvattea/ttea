"""Player model: the people who play the exergames."""

from dataclasses import dataclass, fields
from datetime import datetime
from typing import ClassVar, Dict, List


def initialize_reflexive(cls):
    """Fill the reflection lists of a dataclass (class decorator).

    Parameters
    ----------
    cls : type
        Dataclass to decorate; it must already be a dataclass.

    Returns
    -------
    type
        The same class, with ``PROPERTIES`` and ``DATA_PROPERTIES``
        set.

    Notes
    -----
    ``PROPERTIES`` receives the names of the dataclass fields, in
    declaration order (``ClassVar`` names are not fields).
    ``DATA_PROPERTIES`` receives the default value of each ``init``
    field; a field without a default contributes
    ``dataclasses.MISSING``.
    """
    cls.PROPERTIES = [field.name for field in fields(cls)]
    cls.DATA_PROPERTIES = [
        field.default for field in fields(cls) if field.init
    ]
    return cls


@initialize_reflexive
@dataclass
class Player:
    """Model for player data.

    Attributes
    ----------
    id : int
        Unique identifier for the player.
    name : str
        Name of the player.
    birth_date : datetime
        Player's birth date.
    observation : str
        Additional observations about the player.
    PROPERTIES : list[str], class attribute
        Field names, filled by ``initialize_reflexive``.
    DATA_PROPERTIES : list, class attribute
        Field defaults, filled by ``initialize_reflexive``.

    Methods
    -------
    is_valid()
        Check whether the player's data is valid.
    set_data(data)
        Update the player's data from a dictionary.
    get_data()
        Return the player's data as a one-item list.

    Examples
    --------
    >>> from datetime import datetime
    >>> player = Player(1, "John", datetime(2000, 1, 1), "")
    >>> player.is_valid()
    True
    >>> player.get_data()[0]["name"]
    'John'
    """

    id: int
    name: str
    birth_date: datetime
    observation: str

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
        """Check whether the player's data is valid.

        Returns
        -------
        bool
            True if the player's data is valid, False otherwise.

        Notes
        -----
        A player is valid when ``id`` is an int, ``name`` is not blank,
        ``birth_date`` is not None and no other field (``observation``)
        is None.
        """
        if self.id is None or not isinstance(self.id, int):
            return False

        if not self.name or not self.name.strip():
            return False

        if self.birth_date is None:
            return False

        strong_fields = {"id", "name", "birth_date"}

        for prop in self.PROPERTIES:
            if prop not in strong_fields:
                value = getattr(self, prop)
                if value is None:
                    return False

        return True

    def set_data(self, data: Dict) -> None:
        """Update the fields from a dictionary.

        Parameters
        ----------
        data : dict
            Values keyed by field name. Keys that are not fields are
            ignored, and fields missing from ``data`` keep their value.

        Notes
        -----
        No validation or type conversion is done.
        """
        for prop in self.PROPERTIES:
            if prop in data:
                setattr(self, prop, data[prop])

    def get_data(self) -> List[Dict]:
        """Return the field values as a one-item list.

        Returns
        -------
        list[dict]
            A list with one dictionary that maps each name of
            ``PROPERTIES`` to its current value.
        """
        info = {prop: getattr(self, prop) for prop in self.PROPERTIES}
        return [info]
