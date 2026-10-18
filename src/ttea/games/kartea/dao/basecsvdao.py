"""Generic DAO for the per-player CSV files of KarTEA.

Each player has one file per data type in the players folder:
``{player_id}_{name}_{SUFFIX}.csv`` (e.g. ``1_ana_kartea_session.csv``).
Loading, file naming, insert, update, delete, select and list are
implemented here only once; subclasses define just the model, the
suffix and how to build the object from a CSV row.
"""

import csv
import os
import re
from dataclasses import Field, fields
from typing import Any, TypeVar

from ttea.dao import DAO
from ttea.games.kartea.util.karteapathconfig import KarteaPathConfig
from ttea.util import CSVHandler

T = TypeVar("T")


def _is_annotated_as(model_field: Field, kind: type) -> bool:
    """Check whether a dataclass field is annotated exactly as ``kind``.

    Accepts the evaluated annotation (``int``) and the string annotation
    (``"int"``), which is what the dataclass stores when the model
    module uses ``from __future__ import annotations``.

    Parameters
    ----------
    model_field : Field
        Dataclass field to inspect.
    kind : type
        Expected type (``int``, ``float``, ``bool``...).

    Returns
    -------
    bool
        True if the annotation is ``kind`` or its name.
    """
    annotation = model_field.type
    return annotation is kind or annotation == kind.__name__


class BaseCsvDAO(DAO[T]):
    """CRUD of a model stored in one CSV file per player.

    Attributes
    ----------
    model : type, class attribute
        Model dataclass (with PROPERTIES and ``get_data()``). Defined by
        the subclass.
    suffix : str, class attribute
        File name suffix, e.g. "kartea_session". Defined by the
        subclass.
    single_row : bool, class attribute
        True when the file has a single row per player (the key is the
        player id, e.g. configuration). False (default): one row per
        record, with an incremental id (sessions, details).
    csv_handler : CSVHandler
        Reads/writes in the T-TEA format (``;``, UTF-8 with BOM).
    cache : dict[int, T]
        Loaded objects, by key (record id or player id).
    file_map : dict[int, str]
        Player id -> path of the player's file.
    next_id : int
        Next free id (used only when ``single_row`` is False).
    int_properties : list[str]
        Fields annotated as ``int``, converted from text on load.
    float_properties : list[str]
        Fields annotated as ``float``, converted from text on load.
    bool_properties : list[str]
        Fields annotated as ``bool``, converted from text on load.

    Notes
    -----
    Subclasses must define ``model`` and ``suffix`` (and ``single_row``
    when needed) and implement ``_deserialize(row, player_id)``, which
    builds the object from a CSV row (None = skip the row). They may
    override ``_player(obj)`` (owner of the object, which defines the
    file; default ``obj.player``) and ``_is_valid(obj)``.

    Creating the DAO loads all the files of its suffix into the cache
    (``load_all``).
    """

    model: type
    suffix: str = ""
    single_row: bool = False

    def __init__(self) -> None:
        self.csv_handler = CSVHandler()
        self.cache: dict[int, T] = {}
        self.file_map: dict[int, str] = {}
        self.next_id: int = 1

        model_fields = fields(self.model)
        self.int_properties = [
            f.name for f in model_fields if _is_annotated_as(f, int)
        ]
        self.bool_properties = [
            f.name for f in model_fields if _is_annotated_as(f, bool)
        ]
        self.float_properties = [
            f.name for f in model_fields if _is_annotated_as(f, float)
        ]

        self.load_all()

    # ======================
    # Subclass hooks
    # ======================
    def _deserialize(self, row: dict[str, str], player_id: int) -> T | None:
        """Build the model object from a CSV row (subclass hook).

        Parameters
        ----------
        row : dict[str, str]
            CSV row, keyed by column name.
        player_id : int
            Player id taken from the file name.

        Returns
        -------
        T | None
            The object, or None to skip the row.

        Raises
        ------
        NotImplementedError
            Always, in the base class.
        """
        raise NotImplementedError

    def _player(self, obj: T):
        """Return the player who owns the object.

        Default: ``obj.player``. The player defines the file.
        """
        return obj.player

    def _is_valid(self, obj: T) -> bool:
        """Validate the object before writing.

        Default: the object has a valid player.
        """
        player = self._player(obj)
        return bool(player and player.is_valid())

    def _key(self, obj: T) -> int:
        """Return the object's key in the cache and in the file.

        Returns
        -------
        int
            The player id when ``single_row`` is True, else ``obj.id``.
        """
        return self._player(obj).id if self.single_row else obj.id

    def _row_key(self, row: dict[str, str]) -> int:
        """Return the key of a CSV row (same rule as ``_key``)."""
        column = "player" if self.single_row else "id"
        return self._to_int(row.get(column))

    def _serialize(self, obj: T) -> dict[str, Any]:
        """Return the CSV row of the object.

        References become ids (see ReflexiveModel.get_data).
        """
        return obj.get_data()[0]

    # ======================
    # Conversions
    # ======================
    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        """Convert a value to int, returning ``default`` on failure."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        """Convert a CSV decimal to float (``default`` on failure).

        Accepts a dot or a comma as decimal separator ("0.5" or "0,5").
        """
        try:
            return float(str(value).strip().replace(",", "."))
        except (TypeError, ValueError):
            return default

    def _convert(self, prop: str, value: str) -> Any:
        """Convert the CSV text according to the field type.

        Bool fields are True only for the text "true"
        (case-insensitive); fields that are not int, float or bool keep
        the text.
        """
        if prop in self.int_properties:
            return self._to_int(value)
        if prop in self.float_properties:
            return self._to_float(value)
        if prop in self.bool_properties:
            return str(value).strip().lower() == "true"
        return value

    def _plain_kwargs(self, row: dict[str, str], skip=()) -> dict[str, Any]:
        """Return the row's simple fields, converted, except ``skip``.

        Only columns that are model PROPERTIES and exist in the row are
        returned.
        """
        return {
            prop: self._convert(prop, row[prop])
            for prop in self.model.PROPERTIES
            if prop not in skip and prop in row
        }

    # ======================
    # Files
    # ======================
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Return the player name made safe for a file name.

        Parameters
        ----------
        name : str
            Player name.

        Returns
        -------
        str
            The name stripped and lowercased, with every character that
            is not a letter, digit, ``_`` or ``-`` replaced by ``_``.

        Examples
        --------
        >>> BaseCsvDAO.sanitize_filename(" André Avô ")
        'andré_avô'
        """
        return re.sub(r"[^\w\-]", "_", name.lower().strip())

    def get_filename(self, obj: T) -> str:
        """Return the file path of the player who owns ``obj``.

        Parameters
        ----------
        obj : T
            Model object.

        Returns
        -------
        str
            ``KARTEA_PLAYER_DIR/{player_id}_{sanitized_name}_{suffix}.csv``.
        """
        player = self._player(obj)
        filename = (
            f"{player.id}_{self.sanitize_filename(player.name)}_"
            f"{self.suffix}.csv"
        )
        return str(KarteaPathConfig.KARTEA_PLAYER_DIR / filename)

    def _read_rows(self, filename: str) -> list[dict[str, str]]:
        """Read the CSV rows as dicts (empty if the file is missing)."""
        if not os.path.exists(filename):
            return []
        return self.csv_handler.read_csv(filename, as_dict=True)

    def _write_rows(self, filename: str, rows: list[dict]) -> None:
        """Rewrite the whole file, with PROPERTIES as the header."""
        self.csv_handler.write_csv(
            filename, rows, headers=self.model.PROPERTIES
        )

    def _can_append(self, filename: str) -> bool:
        """Check whether a row can be appended without a rewrite.

        Requires an existing, non-empty file ending in a line break, in
        UTF-8 and with the model's current header. Otherwise (new file,
        old columns, saved by another program...) the file is rewritten
        as a whole, which also migrates the header.

        Returns
        -------
        bool
            True if appending is safe.
        """
        try:
            with open(filename, "rb") as f:
                f.seek(0, os.SEEK_END)
                if f.tell() == 0:
                    return False
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    return False
            with open(filename, newline="", encoding="utf-8-sig") as f:
                header = next(
                    csv.reader(f, dialect=self.csv_handler.dialect), None
                )
        except (OSError, UnicodeDecodeError, csv.Error):
            return False
        return header == list(self.model.PROPERTIES)

    def _append_row(self, filename: str, row: dict) -> None:
        """Append a row to the end of the file (append mode).

        Avoids reading and rewriting the whole CSV for every event,
        which got slower as the file grew. Falls back to a full rewrite
        when ``_can_append`` is False.

        Raises
        ------
        Exception
            Any error while appending is logged and re-raised.
        """
        if not self._can_append(filename):
            self._write_rows(filename, self._read_rows(filename) + [row])
            return
        try:
            with open(filename, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(
                    f,
                    fieldnames=self.model.PROPERTIES,
                    dialect=self.csv_handler.dialect,
                ).writerow(row)
        except Exception as e:
            self.csv_handler.log.log_error(
                f"Failed to append to CSV {filename}: {e}"
            )
            raise

    # ======================
    # Loading
    # ======================
    def load_all(self) -> None:
        """Load the ``*_*_{suffix}.csv`` files into the cache.

        Notes
        -----
        - Ensures the KarTEA folders exist first.
        - The player id is the number before the first ``_`` of the file
          name; files without it are skipped.
        - Rows for which ``_deserialize`` returns None are skipped.
        - With incremental ids, ``next_id`` becomes the highest key + 1.
        """
        KarteaPathConfig.ensure_kartea_dirs()
        for file_path in KarteaPathConfig.KARTEA_PLAYER_DIR.glob(
            f"*_*_{self.suffix}.csv"
        ):
            player_id = self._to_int(file_path.stem.split("_")[0], None)
            if player_id is None:
                continue
            for row in self._read_rows(str(file_path)):
                obj = self._deserialize(row, player_id)
                if obj is None:
                    continue
                key = self._key(obj)
                self.cache[key] = obj
                self.file_map[player_id] = str(file_path)
                if not self.single_row:
                    self.next_id = max(self.next_id, key + 1)

    # ======================
    # CRUD
    # ======================
    def insert(self, obj: T) -> int | bool | None:
        """Write a new record and return its key.

        Parameters
        ----------
        obj : T
            Object to insert. With incremental ids, ``obj.id`` is
            overwritten with ``next_id``.

        Returns
        -------
        int | bool | None
            The key of the record, or False if the object is invalid.

        Notes
        -----
        Records with incremental ids are appended to the end of the
        file; in ``single_row`` mode the file is (re)created with the
        row.
        """
        if not self._is_valid(obj):
            return False

        if not self.single_row:
            obj.id = self.next_id
            self.next_id += 1
        key = self._key(obj)

        filename = self.get_filename(obj)
        self.file_map[self._player(obj).id] = filename

        row = self._serialize(obj)
        if self.single_row:
            self._write_rows(filename, [row])
        else:
            self._append_row(filename, row)

        self.cache[key] = obj
        return key

    def update(self, obj: T) -> bool:
        """Rewrite the object's row (and the file name).

        Parameters
        ----------
        obj : T
            Object with the new data.

        Returns
        -------
        bool
            True if updated; False if the object is invalid or its key
            is not in the cache.

        Notes
        -----
        If the player's name changed, the file is renamed to the new
        sanitized name. If no row has the object's key, the row is
        appended.
        """
        key = self._key(obj) if self._is_valid(obj) else None
        if key is None or key not in self.cache:
            return False

        player_id = self._player(obj).id
        old_filename = self.file_map.get(player_id)
        filename = self.get_filename(obj)
        if old_filename and old_filename != filename:
            if os.path.exists(old_filename):
                os.rename(old_filename, filename)
        self.file_map[player_id] = filename

        self.cache[key] = obj

        row = self._serialize(obj)
        rows = self._read_rows(filename)
        for i, existing in enumerate(rows):
            if self._row_key(existing) == key:
                rows[i] = row
                break
        else:
            rows.append(row)
        self._write_rows(filename, rows)
        return True

    def delete(self, obj_id: int) -> bool:
        """Remove the record; delete the file if it becomes empty.

        Parameters
        ----------
        obj_id : int
            Key of the record.

        Returns
        -------
        bool
            True if removed from the file; False if the key is unknown
            or the player has no file.

        Notes
        -----
        The record is removed from the cache even when the player has no
        file mapped (in that case False is returned).
        """
        obj = self.cache.get(obj_id)
        if obj is None:
            return False

        player_id = self._player(obj).id
        filename = self.file_map.get(player_id)
        del self.cache[obj_id]
        if not filename:
            return False

        rows = [
            row
            for row in self._read_rows(filename)
            if self._row_key(row) != obj_id
        ]
        if rows:
            self._write_rows(filename, rows)
        else:
            if os.path.exists(filename):
                os.remove(filename)
            self.file_map.pop(player_id, None)
        return True

    def select(self, obj_id: int) -> T | None:
        """Return the record with the given key, from the cache.

        Parameters
        ----------
        obj_id : int
            Key of the record (record id or player id).

        Returns
        -------
        T | None
            The record, or None if not found.
        """
        return self.cache.get(obj_id)

    def list(self) -> list[T]:
        """Return all records in the cache.

        Returns
        -------
        list[T]
            The cached records, in loading/insertion order.
        """
        return list(self.cache.values())
