"""Entry point of ``uv run tests``: runs the test suite headless."""

import os
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parents[2] / "tests"


def main() -> None:
    """Discover and run every test module under ``tests/``.

    Notes
    -----
    Uses ``unittest`` discovery with its default pattern
    (``test*.py``). Extra command-line arguments go to ``unittest``
    (e.g. ``-v``). Qt and SDL use headless drivers (``offscreen`` and
    ``dummy``) unless already set, so no window or display is needed.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    unittest.main(
        module=None,
        argv=[sys.argv[0], "discover", "-s", str(TESTS_DIR), *sys.argv[1:]],
    )
