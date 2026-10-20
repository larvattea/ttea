"""CSV persistence of players, one file per player."""

import os
import re
from dataclasses import fields
from datetime import datetime
from typing import Dict, List, Optional

import portalocker

from ttea.dao import DAO
from ttea.model import Player
from ttea.util import CSVHandler, PathConfig


class PlayerCsvDAO(DAO[Player]):
    """DAO for Player entities, one CSV file per record.

    Persists each player in its own CSV file named after its ID and
    sanitized name, and keeps all players in an in-memory cache loaded
    when the DAO is created.

    Attributes
    ----------
    csv_handler : CSVHandler
        Utility for reading and writing CSV data.
    players : dict[int, Player]
        In-memory cache by ID.
    file_map : dict[int, str]
        CSV file path by ID.
    int_properties : list[str]
        Names of the ``Player`` fields typed ``int``.
    bool_properties : list[str]
        Names of the ``Player`` fields typed ``bool``.

    Methods
    -------
    insert(obj)
        Persist a new player and return its ID.
    update(obj)
        Update an existing player, renaming its file if needed.
    delete(obj_id)
        Remove a player and its CSV file.
    select(obj_id)
        Return a player by ID from the cache.
    list()
        Return all cached players.
    search_players(query="")
        Return the players whose ID or name contains ``query``.

    Notes
    -----
    Files are named ``<id>_<sanitized name>_player.csv`` and stored in
    the player directory of ``PathConfig``.

    ``birth_date`` is read with ``datetime.fromisoformat``; an empty
    value is kept as an empty string.
    """

    def __init__(self) -> None:
        self.csv_handler = CSVHandler()
        self.players: Dict[int, Player] = {}
        self.file_map: Dict[int, str] = {}
        self.int_properties = [f.name for f in fields(Player) if f.type == int]
        self.bool_properties = [
            f.name for f in fields(Player) if f.type == bool
        ]
        self.load_all_players()

    def generate_next_id(self) -> int:
        """Return the next available player ID.

        Returns
        -------
        int
            The highest cached ID plus 1, or 1 if the cache is empty.
        """
        if not self.players:
            return 1
        return max(self.players.keys()) + 1

    def write_with_lock(
        self, filepath: str, data: List[Dict], headers: List[str]
    ):
        """Write rows to a CSV file while holding an exclusive lock.

        Parameters
        ----------
        filepath : str
            Full path to the target CSV file.
        data : list[dict]
            Rows to write, one dictionary per row.
        headers : list[str]
            Ordered column names; a header row is written first.

        Raises
        ------
        portalocker.exceptions.LockException
            If the lock cannot be acquired within 10 seconds.

        Notes
        -----
        The user directories are created if needed. The file is opened
        by ``portalocker.Lock`` in mode ``"w"`` with Python's defaults,
        so it uses the platform's default encoding and newline
        translation, unlike ``CSVHandler.write_csv`` with a path (UTF-8
        with BOM).
        """
        PathConfig.ensure_dirs()
        with portalocker.Lock(filepath, mode="w", timeout=10) as f:
            self.csv_handler.write_csv(f, data, headers)

    def insert(self, obj: Player) -> int:
        """Insert a new player and write its CSV file.

        Parameters
        ----------
        obj : Player
            The player to persist. An ``id`` of 0 or less is replaced in
            place by ``generate_next_id()``.

        Returns
        -------
        int
            The player ID on success, or 0 if ``obj`` is not valid or
            its ID already exists.
        """
        if not obj.is_valid():
            return 0

        if obj.id <= 0:
            obj.id = self.generate_next_id()

        if obj.id in self.players:
            return 0

        self.players[obj.id] = obj
        filename = self.get_filename(obj)
        self.file_map[obj.id] = filename
        self.write_with_lock(filename, obj.get_data(), Player.PROPERTIES)
        return obj.id

    def update(self, obj: Player) -> bool:
        """Update an existing player and rewrite its file.

        Parameters
        ----------
        obj : Player
            The player with updated values.

        Returns
        -------
        bool
            True if updated, False if ``obj`` is not valid or its ID is
            not cached.

        Notes
        -----
        If the file name changes (the name changed), the old file is
        renamed before being rewritten.
        """
        if not obj.is_valid() or obj.id not in self.players:
            return False

        old_filename = self.file_map.get(obj.id)
        new_filename = self.get_filename(obj)

        if old_filename != new_filename and os.path.exists(old_filename):
            os.rename(old_filename, new_filename)

        self.players[obj.id] = obj
        self.file_map[obj.id] = new_filename
        self.write_with_lock(new_filename, obj.get_data(), Player.PROPERTIES)
        return True

    def delete(self, obj_id: int) -> bool:
        """Delete a player and remove its CSV file.

        Parameters
        ----------
        obj_id : int
            ID of the player to delete.

        Returns
        -------
        bool
            True if deleted, False if the ID is not cached.
        """
        if obj_id not in self.players:
            return False

        filename = self.file_map.pop(obj_id, None)
        self.players.pop(obj_id, None)

        if filename and os.path.exists(filename):
            os.remove(filename)
        return True

    def select(self, obj_id: int) -> Optional[Player]:
        """Return a player from the in-memory cache.

        Parameters
        ----------
        obj_id : int
            The player ID to look up.

        Returns
        -------
        Player | None
            The player, or None if the ID is not cached.
        """
        return self.players.get(obj_id)

    def list(self) -> List[Player]:
        """Return all cached players.

        Returns
        -------
        list[Player]
            The cached players, in cache order.
        """
        return list(self.players.values())

    def sanitize_filename(self, name: str) -> str:
        """Make a player name safe for file names.

        Parameters
        ----------
        name : str
            Original name.

        Returns
        -------
        str
            The name stripped and lowercased, with every character that
            is not a word character or ``-`` replaced by ``_``.

        Examples
        --------
        >>> dao = object.__new__(PlayerCsvDAO)
        >>> dao.sanitize_filename(" Ana Maria! ")
        'ana_maria_'
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, player: Player) -> str:
        """Return the full path of a player's CSV file.

        Parameters
        ----------
        player : Player
            The player.

        Returns
        -------
        str
            Path of ``<id>_<sanitized name>_player.csv`` in the player
            directory.
        """
        sanitized_name = self.sanitize_filename(player.name)
        filename = f"{player.id}_{sanitized_name}_player.csv"
        return PathConfig.player(filename)

    def load_all_players(self) -> None:
        """Load every player CSV file into the cache.

        Notes
        -----
        Reads each ``*_player.csv`` file of the player directory; empty
        or unreadable files are skipped. Only the first row is used.
        Integer fields that are not plain digits (including negative
        numbers) become 0, and boolean fields are True only for
        ``"true"`` (any case).
        """
        PathConfig.ensure_dirs()
        for file_path in PathConfig.PLAYERS_DIR.glob("*_player.csv"):
            player_data = self.csv_handler.read_csv(
                str(file_path), as_dict=True
            )
            if not player_data:
                continue

            row = player_data[0]
            player_kwargs = {}
            for prop in Player.PROPERTIES:
                if prop in row:
                    if prop == "birth_date" and row[prop]:
                        player_kwargs[prop] = datetime.fromisoformat(row[prop])
                    elif prop in self.int_properties:
                        player_kwargs[prop] = (
                            int(row[prop]) if row[prop].isdigit() else 0
                        )
                    elif prop in self.bool_properties:
                        player_kwargs[prop] = row[prop].lower() == "true"
                    else:
                        player_kwargs[prop] = row[prop]

            player = Player(**player_kwargs)
            self.players[player.id] = player
            self.file_map[player.id] = str(file_path)

    def search_players(self, query: str = "") -> List[Player]:
        """Return cached players, optionally filtered.

        Parameters
        ----------
        query : str, optional
            Text searched, case-insensitively, in the ID and the name. A
            blank query returns every player. Default is ``""``.

        Returns
        -------
        list[Player]
            The matching players.
        """
        all_players = list(self.players.values())

        if not query.strip():
            return all_players

        q = query.lower().strip()
        return [
            p for p in all_players if q in str(p.id) or q in p.name.lower()
        ]
