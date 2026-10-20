"""View factory of the Kartea game.

This package builds the KarTEA register screens (views), wiring each
view to its controller and services. Developed by the Larva UDESC
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
KarteaViewFactory
    Creates the KarTEA configuration list and edit screens.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development. Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "KarteaViewFactory",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .karteaviewfactory import KarteaViewFactory
