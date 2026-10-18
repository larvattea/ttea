"""Themes of the KarTEA game (pygame side).

This package provides the track color scheme, built from the palette
chosen in the player's configuration. Developed by the Larva UDESC
team.

Attributes
----------
__version__ : str
    The current version of the package.
__date__ : str
    The release date of this version.
__author__ : str
    The development team.
__license__ : str
    The license under which the package is distributed.

See Also
--------
KarTEATheme
    Track colors (finish line, grass, rumble, road) as pygame colors.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larva-udesc/udesc_ttea_view
"""

__all__ = [
    "KarTEATheme",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .karteatheme import KarTEATheme
