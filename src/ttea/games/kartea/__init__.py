"""KarTEA exergame of the T-TEA console.

The player drives a car along a pseudo-3D road by moving the feet in
front of the camera, collecting targets and avoiding obstacles.

The game has two sides:

- the configuration screens (PySide6, MVC): ``model``, ``dao``,
  ``service``, ``controller``, ``view``, ``factory`` and the generated
  ``ui``;
- the game itself (pygame), started by ``main``: ``gamecontroller``,
  ``gamecore``, ``gamemodel``, ``gameview``, ``gameui``, ``gameutil``
  and ``gametheme``.

``util`` holds the paths, defaults and resource fields shared by both.
"""
