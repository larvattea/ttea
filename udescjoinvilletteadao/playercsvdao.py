import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Union

# Local module import
from udescjoinvilletteadao import DAO
from udescjoinvilletteamodel import Player
from udescjoinvilletteautil import CSVHandler, PathConfig


# DAO Implementation
class PlayerCsvDAO(DAO):
    """Data Access Object for managing Player data in CSV files.

    This class implements the DAO interface to handle CRUD operations
    for Player objects, storing data in CSV files. It maintains an
    in-memory cache of players and maps player IDs to filenames.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV files.
    players : Dict[int, Player]
        In-memory cache of Player objects, keyed by player ID.
    file_map : Dict[int, str]
        Maps player IDs to their corresponding CSV file paths.

    Methods
    -------
    __init__()
        Initializes the PlayerCsvDAO with an empty cache and loads
        existing players from CSV files.
    sanitize_filename(name: str) -> str
        Sanitizes a player name for safe file naming.
    get_filename(player: Player) -> str
        Generates a filename for a player based on ID and name.
    load_all_players() -> None
        Loads all player data from CSV files into memory.
    insert(obj: Player) -> Optional[Union[int, str, bool]]
        Inserts a new player and creates a corresponding CSV file.
    update(obj: Player) -> Optional[Union[int, bool]]
        Updates player data and renames the file if the name changes.
    delete(obj_id: int) -> Optional[Union[int, bool]]
        Deletes a player from memory and removes their CSV file.
    select(obj_id: int) -> Optional[Player]
        Retrieves a player by their ID.
    list() -> List[Player]
        Returns a list of all players.
    """

    def __init__(self) -> None:
        """Initialize the PlayerCsvDAO.

        Sets up the CSV handler, initializes the players dictionary,
        and loads all existing player data from CSV files into memory.

        Returns
        -------
        None

        Notes
        -----
        Creates necessary directories if they do not exist.
        """
        self.csv_handler = CSVHandler()
        self.players: Dict[int, Player] = {}
        # Maps player ID to filename
        self.file_map: Dict[int, str] = {}
        self.load_all_players()

    def sanitize_filename(self, name: str) -> str:
        """Sanitize player name for safe file naming.

        Parameters
        ----------
        name : str
            The player's name to be sanitized.

        Returns
        -------
        str
            A sanitized version of the name suitable for file naming.

        Notes
        -----
        Removes non-alphanumeric characters and converts to lowercase.
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, player: Player) -> str:
        """Generate filename using player ID and sanitized name.

        Parameters
        ----------
        player : Player
            The player object for which to generate a filename.

        Returns
        -------
        str
            The full path to the player's CSV file.

        Notes
        -----
        Combines player ID and sanitized name with '_player.csv' suffix.
        """
        sanitized_name = self.sanitize_filename(player.name)
        filename = f"{player.id}_{sanitized_name}_player.csv"
        return PathConfig.player(filename)

    def load_all_players(self) -> None:
        """Load all player CSV files into memory.

        Iterates through all CSV files in the players directory,
        reads their data, and populates the players dictionary.

        Notes
        -----
        Assumes CSV files follow the naming convention
        '<id>_<name>_player.csv' and contain valid player data.
        """
        PathConfig.create_directories()
        for file_path in PathConfig.players_dir.glob("*_player.csv"):
            player_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if player_data:
                player = Player(
                    id=int(player_data[0]["id"]),
                    name=player_data[0]["name"],
                    birth_date=datetime.fromisoformat(
                        player_data[0]["birth_date"]
                    ),
                    observation=player_data[0]["observation"],
                )
                self.players[player.id] = player
                self.file_map[player.id] = str(file_path)

    def insert(self, obj: Player) -> Optional[Union[int, str, bool]]:
        """Insert a new player and create corresponding CSV file.

        Parameters
        ----------
        obj : Player
            The player object to be inserted.

        Returns
        -------
        Optional[Union[int, str, bool]]
            The player ID if successful, False if invalid or duplicate.

        Notes
        -----
        Checks if the player is valid and not already in the cache.
        Writes player data to a new CSV file.
        """
        if not obj.is_valid():
            return False
        if obj.id in self.players:
            return False
        self.players[obj.id] = obj
        filename = self.get_filename(obj)
        self.file_map[obj.id] = filename
        self.csv_handler.write_csv(
            filename, obj.get_player_data(), Player.PROPERTIES
        )
        return obj.id

    def update(self, obj: Player) -> Optional[Union[int, bool]]:
        """Update player data and rename file if name changed.

        Parameters
        ----------
        obj : Player
            The player object with updated data.

        Returns
        -------
        Optional[Union[int, bool]]
            True if update is successful, False if invalid or not found.

        Notes
        -----
        Renames the CSV file if the player's name has changed.
        Overwrites the existing CSV file with updated data.
        """
        if not obj.is_valid() or obj.id not in self.players:
            return False

        old_filename = self.file_map.get(obj.id)
        new_filename = self.get_filename(obj)

        # If name changed, rename the file
        if old_filename and old_filename != new_filename:
            os.rename(old_filename, new_filename)
            self.file_map[obj.id] = new_filename

        self.players[obj.id] = obj
        self.csv_handler.write_csv(
            new_filename, obj.get_player_data(), Player.PROPERTIES
        )
        return True

    def delete(self, obj_id: int) -> Optional[Union[int, bool]]:
        """Delete player from memory and remove their CSV file.

        Parameters
        ----------
        obj_id : int
            The ID of the player to delete.

        Returns
        -------
        Optional[Union[int, bool]]
            True if deletion is successful, False if player not found.

        Notes
        -----
        Removes the player from the in-memory cache and deletes their
        CSV file from the filesystem.
        """
        if obj_id not in self.players:
            return False
        filename = self.file_map.get(obj_id)
        del self.players[obj_id]
        del self.file_map[obj_id]
        if filename:
            os.remove(filename)
            return True
        return False

    def select(self, obj_id: int) -> Optional[Player]:
        """Retrieve a player by ID.

        Parameters
        ----------
        obj_id : int
            The ID of the player to retrieve.

        Returns
        -------
        Optional[Player]
            The Player object if found, None otherwise.

        Notes
        -----
        Retrieves the player from the in-memory cache.
        """
        return self.players.get(obj_id)

    def list(self) -> List[Player]:
        """List all players.

        Returns
        -------
        List[Player]
            A list containing all Player objects in the cache.

        Notes
        -----
        Returns a list of all players currently loaded in memory.
        """
        return list(self.players.values())
