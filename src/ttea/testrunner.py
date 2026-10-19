"""Entry point of ``uv run tests``: runs the test suite headless."""

import os
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parents[2] / "tests"


def main() -> None:
    """Discover and run every ``test_*.py`` under ``tests/``.

    Extra command-line arguments go to ``unittest`` (e.g. ``-v``).
    Qt and SDL use headless drivers, so no window or display is needed.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    unittest.main(
        module=None,
        argv=[sys.argv[0], "discover", "-s", str(TESTS_DIR), *sys.argv[1:]],
    )
