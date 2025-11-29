# udescjoinvillettea/service/player_service.py
from datetime import date
from typing import Any, Dict, List, Optional

from udescjoinvilletteadao import PlayerCsvDAO
from udescjoinvilletteamodel import Player


class PlayerService:
    """
    Service layer (MVCS) handling all business rules related to players.

    Attributes
    ----------
    dao : PlayerCsvDAO
        Data access object responsible for persistence operations.
        Defaults to a new ``PlayerCsvDAO`` instance if not provided.

    Methods
    -------
    __init__(dao=None)
        Initializes the service with a DAO instance.
    get_all_players()
        Returns all registered players.
    create_player(data)
        Creates a new player from the provided data dictionary.
    update_player(player_id, data)
        Updates an existing player with the given data.
    delete_player(player_id)
        Deletes a player by its ID.
    find_by_id(player_id)
        Retrieves a player by its ID.
    search_players(query="")
        Searches players by name or ID (case-insensitive).
    """

    def __init__(self, dao: Optional[PlayerCsvDAO] = None):
        """
        Initialize the service with a data access object.

        Parameters
        ----------
        dao : PlayerCsvDAO, optional
            Instance used for persistence. If ``None``, a default
            ``PlayerCsvDAO`` is created.
        """
        self.dao = dao or PlayerCsvDAO()

    def get_all_players(self) -> List[Player]:
        """Return a list of all registered players.

        Returns
        -------
        List[Player]
            Complete list of ``Player`` instances stored in the DAO.
        """
        return self.dao.list()

    def create_player(self, data: Dict[str, Any]) -> Optional[Player]:
        """
        Create a new player from a dictionary of attributes.

        Parameters
        ----------
        data : dict
            Must contain the keys ``name`` (str), ``birth_date`` (date),
            and optionally ``observation`` (str).

        Returns
        -------
        Player or None
            The created ``Player`` instance if validation and insertion
            succeed; ``None`` otherwise.
        """
        player = Player(
            id=0,
            name=data.get("name", "").strip(),
            birth_date=data.get("birth_date"),
            observation=data.get("observation", "").strip(),
        )

        if not player.is_valid():
            return None

        new_id = self.dao.insert(player)
        return self.dao.select(new_id) if new_id > 0 else None

    def update_player(self, player_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing player with new values.

        Parameters
        ----------
        player_id : int
            Identifier of the player to update.
        data : dict
            Dictionary containing updated fields (``name``,
            ``birth_date``, ``observation``). Missing keys keep the
            current value.

        Returns
        -------
        bool
            ``True`` if the player was found, validated, and updated
            successfully; ``False`` otherwise.
        """
        player = self.dao.select(player_id)
        if not player:
            return False

        player.name = data.get("name", player.name).strip()
        player.birth_date = data.get("birth_date", player.birth_date)
        player.observation = data.get(
            "observation", player.observation or ""
        ).strip()

        if not player.is_valid():
            return False

        return self.dao.update(player)

    def delete_player(self, player_id: int) -> bool:
        """Delete a player by its identifier.

        Parameters
        ----------
        player_id : int
            Identifier of the player to be removed.

        Returns
        -------
        bool
            ``True`` if the player was successfully deleted,
            ``False`` otherwise (e.g., player not found).
        """
        return self.dao.delete(player_id)

    def find_by_id(self, player_id: int) -> Optional[Player]:
        """Retrieve a player by its unique identifier.

        Parameters
        ----------
        player_id : int
            The player's ID.

        Returns
        -------
        Player or None
            The matching ``Player`` instance or ``None`` if not found.
        """
        return self.dao.select(player_id)

    def search_players(self, query: str = "") -> List[Player]:
        """
        Search players by name or ID (case-insensitive).

        Parameters
        ----------
        query : str, optional
            Search term. If empty or whitespace-only, returns all
            players.

        Returns
        -------
        List[Player]
            List of players whose ID (as string) or name contain the
            query term.
        """
        all_players = self.get_all_players()
        if not query.strip():
            return all_players

        q = query.lower().strip()
        return [
            p for p in all_players if q in str(p.id) or q in p.name.lower()
        ]
