"""Track color theme of the KarTEA game."""

import pygame

from ttea.games.gametheme.basetheme import BaseTheme
from ttea.games.kartea.util import KarteaPalettes


class KarTEATheme(BaseTheme):
    """Encapsulate the color scheme of the track.

    The colors come from the palette chosen in the player's
    configuration (``KarteaPalettes.ALL``). A palette number that does
    not exist uses the default palette.

    Parameters
    ----------
    palette : int, optional
        Palette number (``GameSettings.PALETTE``). Defaults to
        ``KarteaPalettes.DEFAULT``.

    Attributes
    ----------
    finish : dict[str, pygame.Color]
        ``"dark"`` and ``"light"`` colors of the finish line.
    grass : dict[str, pygame.Color]
        ``"dark"`` and ``"light"`` colors of the grass.
    rumble : dict[str, pygame.Color]
        ``"dark"`` and ``"light"`` colors of the side strip.
    road : dict[str, pygame.Color]
        ``"dark"`` and ``"light"`` colors of the road.

    Examples
    --------
    >>> theme = KarTEATheme(1)
    >>> theme.grass["dark"].g
    150
    >>> KarTEATheme(99).road["dark"].r
    75
    """

    def __init__(self, palette: int = KarteaPalettes.DEFAULT):
        colors = KarteaPalettes.get(palette)
        self.finish = self._to_colors(colors.finish)
        self.grass = self._to_colors(colors.grass)
        self.rumble = self._to_colors(colors.rumble)
        self.road = self._to_colors(colors.road)

    @staticmethod
    def _to_colors(tones: dict) -> dict[str, pygame.Color]:
        """Convert RGB tones to ``pygame.Color`` values.

        ``{"dark": (r, g, b), ...}`` -> ``{"dark": pygame.Color, ...}``.
        """
        return {tone: pygame.Color(*rgb) for tone, rgb in tones.items()}
