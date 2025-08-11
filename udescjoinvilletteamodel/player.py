from dataclasses import dataclass, fields
from datetime import datetime
from typing import ClassVar, Dict, List


def initialize_reflexive(cls):
    """Decorator to statically initialize player reflection data.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with initialized PROPERTIES and DATA_PROPERTIES
        attributes.

    Notes
    -----
    - Adds the list of field names to `PROPERTIES`.
    - Adds the default values of initializable fields to `DATA_PROPERTIES`.
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
    observation : str, optional
        Additional observations about the player (default is "").
    PROPERTIES : ClassVar[list[str]]
        Static list of the class's field names.
    DATA_PROPERTIES : ClassVar[list]
        Static list of default values for initializable fields.

    Methods
    -------
    is_valid()
        Checks if the player's data is valid.
    set_player_data(self, data: Dict)
        Updates the player's data from a dictionary.
    def get_player_data():
        Returns the player's data as a list of dictionaries.

    Examples
    --------
    >>> from datetime import datetime
    >>> player = Player(id=1, name="John", birth_date=datetime(2000, 1, 1))
    >>> player.is_valid()
    True
    >>> player.get_player_data()
    [{'id': 1, 'name': 'John', 'birth_date': datetime(2000, 1, 1),
    'observation': ''}]
    """

    id: int
    name: str
    birth_date: datetime
    observation: str = ""

    PROPERTIES: ClassVar[list[str]] = []
    DATA_PROPERTIES: ClassVar[list] = []

    def is_valid(self) -> bool:
        """Checks if the player's data is valid.

        Returns
        -------
        bool
            True if the player's name and birth date are provided, False
            otherwise.

        Notes
        -----
        - A player is considered valid if `name` is not an empty string and
        `birth_date` is not None.
        """
        return self.name and self.birth_date

    def set_player_data(self, data: Dict) -> None:
        """Updates the player's data from a dictionary.

        Parameters
        ----------
        data : Dict
            Dictionary containing player data with the following keys:
            - 'id': int
            - 'name': str
            - 'birth_date': datetime
            - 'observation': str

        Returns
        -------
        None

        Notes
        -----
        - Replaces the player's attributes with the values provided in
        the dictionary.
        - Does not perform validation on the provided data.
        """

        self.id = data["id"]
        self.name = data["name"]
        self.birth_date = data["birth_date"]
        self.observation = data["observation"]

    def get_player_data(self) -> List[Dict]:
        """Returns the player's data as a list of dictionaries.

        Returns
        -------
        List[Dict]
            List containing a single dictionary with the player's data,
            including:
            - 'id': int
            - 'name': str
            - 'birth_date': datetime
            - 'observation': str

        Notes
        -----
        - The method returns a list to maintain consistency with potential
        future implementations that may return multiple records.
        """
        info = {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date,
            "observation": self.observation,
        }

        return [info]
