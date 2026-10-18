"""Loading of game sounds (pygame) from the QRC or from files."""

import io

import pygame
from PySide6.QtCore import QFile, QIODevice

from ttea.games.kartea.util import KarteaPathConfig


class Sound:
    """Utility class to load pygame sounds.

    Supports Qt resources (.qrc) and physical paths, like ``Image``.
    ``pygame.mixer.Sound`` does not open Qt ``:/`` paths: for built-in
    resources, the bytes are read with ``QFile`` and handed to pygame in
    memory.

    Attributes
    ----------
    _cache : dict[str, bytes], class attribute
        Bytes already read, by path. The bytes (not the
        ``pygame.mixer.Sound``) are cached so that each caller gets its
        own Sound: the volume is per object (FeedbackView mutes/unmutes
        the sound) and the menu click must not be affected by it.
    """

    _cache: dict[str, bytes] = {}

    @staticmethod
    def resolve(name: str) -> str:
        """Return the path of sound ``name``.

        Parameters
        ----------
        name : str
            QRC alias, ``:/...`` path or file path.

        Returns
        -------
        str
            The built-in Qt resource, if it exists; otherwise ``name``
            itself (physical path or already resolved ``:/`` path). ""
            for an empty name.
        """
        if not name:
            return ""
        return KarteaPathConfig.game_builtin_sound(name) or name

    @staticmethod
    def load(name: str) -> pygame.mixer.Sound:
        """Load sound ``name`` (QRC alias, ``:/...`` or file).

        Parameters
        ----------
        name : str
            Sound to load.

        Returns
        -------
        pygame.mixer.Sound
            The sound; a silent sound on error, so that the game does
            not stop because of a missing or invalid sound file.

        Notes
        -----
        Qt resources are read once and cached as bytes (``_cache``).
        Errors are printed to the console, not raised.
        """
        full_path = Sound.resolve(name)
        if not full_path:
            return Sound._silent()

        try:
            if full_path.startswith(":/"):
                data = Sound._cache.get(full_path)
                if data is None:
                    data = Sound._read_qt_resource(full_path)
                    Sound._cache[full_path] = data
                return pygame.mixer.Sound(file=io.BytesIO(data))
            return pygame.mixer.Sound(full_path)
        except Exception as e:
            print(f"[Sound.load] Erro ao carregar '{name}': {e}.")
            return Sound._silent()

    @staticmethod
    def _read_qt_resource(resource_path: str) -> bytes:
        """Read the bytes of a Qt resource via QFile.

        Raises
        ------
        FileNotFoundError
            If the resource cannot be opened.
        """
        file = QFile(resource_path)
        if not file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(
                f"Não foi possível abrir recurso Qt: {resource_path}."
            )
        data = file.readAll().data()
        file.close()
        return data

    @staticmethod
    def _silent() -> pygame.mixer.Sound:
        """Return a very short silent sound (fallback)."""
        return pygame.mixer.Sound(buffer=bytes(64))
