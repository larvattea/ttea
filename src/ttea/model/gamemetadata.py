"""Model for game metadata read from each game's metadata.json.

This module provides the ``GameMetadata`` class, which loads and
validates the metadata file (schema 1.x) of a game, or the manifest of
a ``.ttea`` cartridge, and exposes the data needed by the platform to
list, configure and launch the game.
"""

import json
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

from .language import Language


@dataclass
class GameMetadata:
    """Game metadata read from ``metadata.json`` (schema 1.x).

    Attributes
    ----------
    id : str
        Unique game identifier (e.g. ``"br.udesc.larva.kartea"``).
    version : str
        Game version.
    folder_path : Path
        Folder where the game is installed.
    entrypoint : str
        File run to start the game, relative to the game folder.
    view_factory : str | None
        Full path of the game's view factory class.
    menu_actions : dict[str, dict]
        Actions the game adds to the platform settings menu.
    icon : str | None
        Icon path, relative to the game folder.
    developers : list[str]
        Developer names.
    release_date : str | None
        Release date (ISO date or just the year).
    required_peripherals : list[str]
        Required peripherals (e.g. ``"webcam"``, ``"projector"``).
    localization : dict[str, dict[str, str]]
        Texts per language code (``name``, ``short_description``,
        ``about_the_game``...).
    default_language : str
        Language used when the platform language is not available.
    raw : dict[str, Any]
        Full JSON content, for fields not mapped yet. Default is an
        empty dictionary; it is left out of ``repr``.
    SUPPORTED_SCHEMA_MAJOR : str, class attribute
        Supported major schema version (``"1"``).
    FILENAME : str, class attribute
        Metadata file name (``"metadata.json"``).
    CARTRIDGE_EXTENSION : str, class attribute
        Extension of TSDK game cartridges (``".ttea"``).
    CARTRIDGE_MANIFEST : str, class attribute
        Manifest file name inside a cartridge (``"manifest.json"``).
    """

    SUPPORTED_SCHEMA_MAJOR: ClassVar[str] = "1"
    FILENAME: ClassVar[str] = "metadata.json"
    CARTRIDGE_EXTENSION: ClassVar[str] = ".ttea"
    CARTRIDGE_MANIFEST: ClassVar[str] = "manifest.json"

    id: str
    version: str
    folder_path: Path
    entrypoint: str
    view_factory: Optional[str]
    menu_actions: Dict[str, dict]
    icon: Optional[str]
    developers: List[str]
    release_date: Optional[str]
    required_peripherals: List[str]
    localization: Dict[str, Dict[str, str]]
    default_language: str
    raw: Dict[str, Any] = field(repr=False, default_factory=dict)

    # ---------- loading ----------
    @classmethod
    def load(cls, path: Path) -> "GameMetadata":
        """Read a ``metadata.json`` file and return its metadata.

        Parameters
        ----------
        path : Path
            Path of the ``metadata.json`` file; a ``str`` is also
            accepted.

        Returns
        -------
        GameMetadata
            The game metadata; ``folder_path`` is the folder of the
            file.

        Raises
        ------
        ValueError
            If the JSON is invalid, the major ``schema_version`` is not
            ``SUPPORTED_SCHEMA_MAJOR`` or a required field is missing.
        OSError
            If the file cannot be opened.
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema = str(data.get("schema_version", ""))
        if schema.split(".")[0] != cls.SUPPORTED_SCHEMA_MAJOR:
            raise ValueError(
                f"{path}: schema_version '{schema}' não suportado "
                f"(esperado {cls.SUPPORTED_SCHEMA_MAJOR}.x)"
            )

        try:
            return cls._parse(data, path.parent)
        except KeyError as e:
            raise ValueError(
                f"{path}: campo obrigatório ausente: {e}"
            ) from e

    @classmethod
    def _parse(cls, d: dict, folder: Path) -> "GameMetadata":
        """Build a GameMetadata from the parsed JSON.

        Parameters
        ----------
        d : dict
            Parsed ``metadata.json`` content.
        folder : Path
            Game folder.

        Returns
        -------
        GameMetadata
            The game metadata.

        Raises
        ------
        KeyError
            If ``id``, ``version``, ``runtime``, ``runtime.entrypoint``
            or the ``name`` of a developer is missing.

        Notes
        -----
        Optional fields default to empty values: no ``view_factory``,
        ``icon`` or ``release_date`` gives None; no ``menu_actions``,
        ``developers`` or ``required_peripherals`` gives an empty
        collection. ``localization`` keeps only the entries of
        ``store.localization`` that are dictionaries; its ``default``
        entry (``"en_US"`` if absent) becomes ``default_language``.
        """
        runtime = d["runtime"]
        store = d.get("store", {})
        loc = store.get("localization", {})

        return cls(
            id=d["id"],
            version=d["version"],
            folder_path=folder,
            entrypoint=runtime["entrypoint"],
            view_factory=runtime.get("view_factory"),
            menu_actions=runtime.get("menu_actions") or {},
            icon=(store.get("assets") or {}).get("icon"),
            developers=[
                dev["name"] for dev in store.get("developers") or []
            ],
            release_date=(store.get("release_date") or {}).get("date"),
            required_peripherals=runtime.get("required_peripherals") or [],
            localization={
                k: v for k, v in loc.items() if isinstance(v, dict)
            },
            default_language=loc.get("default", "en_US"),
            raw=d,
        )

    @classmethod
    def load_cartridge(cls, path: Path) -> "GameMetadata":
        """Read the ``manifest.json`` of a ``.ttea`` cartridge.

        Parameters
        ----------
        path : Path
            Path of the ``.ttea`` file; a ``str`` is also accepted.

        Returns
        -------
        GameMetadata
            The game metadata; ``folder_path`` is the folder of the
            file and ``entrypoint`` its name.

        Raises
        ------
        ValueError
            If the file is not a readable ZIP with a ``manifest.json``
            object, ``id`` or ``version`` is missing, or ``name`` (or
            ``description``, when present) is neither a text nor a map
            of language to text.

        Notes
        -----
        The cartridge runs with the external ``tsdk`` command; only the
        data shown on the game launch screen is read here. A cartridge
        has no view factory, menu actions or icon.
        """
        path = Path(path)
        try:
            with zipfile.ZipFile(path) as zf:
                data = json.loads(zf.read(cls.CARTRIDGE_MANIFEST))
        except (
            zipfile.BadZipFile,
            zlib.error,
            EOFError,
            KeyError,
            ValueError,
            NotImplementedError,
            RuntimeError,
            OSError,
        ) as e:
            raise ValueError(f"{path}: cartucho inválido: {e}") from e
        if not isinstance(data, dict):
            raise ValueError(f"{path}: manifest.json deve ser um objeto")

        for key in ("id", "version"):
            if not isinstance(data.get(key), str) or not data[key]:
                raise ValueError(f"{path}: campo obrigatório ausente: '{key}'")

        localization: Dict[str, Dict[str, str]] = {}
        for manifest_key, key in (
            ("name", "name"),
            ("description", "short_description"),
        ):
            if manifest_key == "description" and manifest_key not in data:
                continue
            texts = cls._cartridge_texts(data.get(manifest_key))
            if texts is None:
                raise ValueError(
                    f"{path}: '{manifest_key}' deve ser um texto ou um "
                    f"mapa de idioma para texto"
                )
            for code, value in texts.items():
                localization.setdefault(code, {})[key] = value

        default_language = (
            "en_US" if "en_US" in localization else next(iter(localization))
        )
        return cls(
            id=data["id"],
            version=data["version"],
            folder_path=path.parent,
            entrypoint=path.name,
            view_factory=None,
            menu_actions={},
            icon=None,
            developers=[],
            release_date=None,
            required_peripherals=[],
            localization=localization,
            default_language=default_language,
            raw=data,
        )

    @staticmethod
    def _cartridge_texts(value: Any) -> Optional[Dict[str, str]]:
        """Convert a manifest ``name`` or ``description`` per language.

        Parameters
        ----------
        value : Any
            A text, or a map of BCP 47 tag (``"pt-BR"``, ``"es"``) to
            text.

        Returns
        -------
        dict[str, str] | None
            Texts per platform language code, or None if ``value`` is
            invalid.

        Notes
        -----
        A plain text is used for ``"en_US"``. In a map, each tag becomes
        the platform code it matches exactly or, failing that, the first
        code with the same language prefix (``"pt"`` -> ``"pt_BR"``);
        an exact match wins over a prefix match.
        """
        if isinstance(value, str) and value.strip():
            return {"en_US": value}
        if not isinstance(value, dict) or not value:
            return None

        codes = [lang["code"] for lang in Language.LANGUAGES]
        exact: Dict[str, str] = {}
        by_prefix: Dict[str, str] = {}
        for tag, text in value.items():
            if not isinstance(tag, str) or not isinstance(text, str):
                return None
            if not text.strip():
                return None
            tag = tag.replace("-", "_")
            match = next((c for c in codes if c.lower() == tag.lower()), None)
            if match:
                exact[match] = text
                continue
            prefix = tag.split("_")[0].lower()
            match = next(
                (c for c in codes if c.lower().startswith(prefix + "_")), tag
            )
            by_prefix.setdefault(match, text)
        return {**by_prefix, **exact}

    # ---------- access ----------
    def text(self, lang: str, key: str, default: str = "") -> str:
        """Return a text in a language, falling back to the default.

        Parameters
        ----------
        lang : str
            Language code, e.g. ``"pt_BR"``.
        key : str
            Text key, e.g. ``"name"``.
        default : str, optional
            Value returned when neither language has a non-empty text.
            Default is ``""``.

        Returns
        -------
        str
            The text in ``lang``, else in ``default_language``, else
            ``default``.

        Examples
        --------
        >>> loc = {"en_US": {"name": "Game"}}
        >>> data = {"id": "g", "version": "1",
        ...         "runtime": {"entrypoint": "m.py"},
        ...         "store": {"localization": loc}}
        >>> meta = GameMetadata._parse(data, Path("games/g"))
        >>> meta.text("pt_BR", "name")
        'Game'
        >>> meta.name("es_ES")
        'Game'
        """
        for code in (lang, self.default_language):
            value = self.localization.get(code, {}).get(key)
            if value:
                return value
        return default

    def name(self, lang: str) -> str:
        """Return the display name of the game in a language.

        Parameters
        ----------
        lang : str
            Language code.

        Returns
        -------
        str
            The localized ``name`` text, or the game ``id`` if there is
            none.
        """
        return self.text(lang, "name", self.id)

    @property
    def icon_path(self) -> str:
        """Absolute icon path, or an empty string without an icon."""
        return str(self.folder_path / self.icon) if self.icon else ""

    @property
    def entrypoint_path(self) -> Path:
        """Absolute path of the file that starts the game."""
        return self.folder_path / self.entrypoint

    @property
    def release_year(self) -> str:
        """Release year: the first 4 characters of the release date."""
        return (self.release_date or "")[:4]
