"""Platform-safe blitting of surfaces with per-pixel alpha."""

import sys

import pygame


def alpha_blit_flags() -> int:
    """Return the blit flags for per-pixel-alpha surfaces.

    Returns
    -------
    int
        ``pygame.BLEND_ALPHA_SDL2`` on macOS (SDL2's alpha blitter); 0
        (pygame defaults) elsewhere.
    """
    if sys.platform == "darwin":
        return pygame.BLEND_ALPHA_SDL2
    return 0


def alpha_blit(
    destination: pygame.Surface,
    source: pygame.Surface,
    position,
) -> pygame.Rect:
    """Blit a per-pixel-alpha surface with the platform-safe path.

    Parameters
    ----------
    destination : pygame.Surface
        Surface drawn on.
    source : pygame.Surface
        Surface with per-pixel alpha to draw.
    position : Any
        Position accepted by ``Surface.blit`` (tuple or Rect).

    Returns
    -------
    pygame.Rect
        Area affected, as returned by ``Surface.blit``.
    """
    return destination.blit(
        source,
        position,
        special_flags=alpha_blit_flags(),
    )
