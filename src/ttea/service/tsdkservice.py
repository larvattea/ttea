"""Runtime of ``.ttea`` games: TSDK in its own environment, by uv."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from uv import find_uv_bin

from ttea.util import PathConfig


class TsdkService:
    """Run TSDK, the runtime of ``.ttea`` games, through uv.

    TSDK needs Python 3.14 and versions of MediaPipe, NumPy, OpenCV and
    pygame that conflict with the platform's, so it cannot be a
    dependency of T-TEA. uv builds its environment from ``REQUIREMENT``
    under ``PathConfig.RUNTIME_DIR``: preparing it downloads Python and
    the packages once (internet required), and every game then starts
    offline from that environment.

    Attributes
    ----------
    PYTHON : str, class attribute
        Python version TSDK runs on.
    REQUIREMENT : str, class attribute
        Pinned TSDK source. A source archive, not a git URL, so the
        machine does not need git.
    """

    PYTHON = "3.14"
    REQUIREMENT = (
        "tsdk @ https://github.com/larvattea/tsdk/archive/"
        "83e419f7485f5535b04316c87f3451430c6ee65a.zip"
    )

    @staticmethod
    def uv_executable() -> str:
        """Return the path of the uv executable.

        Returns
        -------
        str
            In development, the uv installed with the platform
            dependencies; in the packaged build, the ``uv`` (``uv.exe``
            on Windows) bundled at the root of the bundle
            (``sys._MEIPASS``).
        """
        if getattr(sys, "frozen", False):
            name = "uv.exe" if sys.platform.startswith("win") else "uv"
            bundle = getattr(sys, "_MEIPASS", Path(sys.executable).parent)
            return str(Path(bundle) / name)
        return find_uv_bin()

    @staticmethod
    def environment() -> Dict[str, str]:
        """Return the process environment for running uv.

        Returns
        -------
        dict[str, str]
            The current environment, with uv's cache, Python
            installations and tools under ``PathConfig.RUNTIME_DIR``.
            Only Python versions installed there are used, and uv
            configuration files of the machine are ignored.
        """
        runtime = PathConfig.RUNTIME_DIR
        return {
            **os.environ,
            "UV_CACHE_DIR": str(runtime / "cache"),
            "UV_PYTHON_INSTALL_DIR": str(runtime / "python"),
            "UV_TOOL_DIR": str(runtime / "tools"),
            "UV_PYTHON_PREFERENCE": "only-managed",
            "UV_NO_CONFIG": "1",
        }

    def _command(self, offline: bool, *tsdk_args: str) -> List[str]:
        """Return the uv command that runs ``tsdk`` with arguments."""
        return [
            self.uv_executable(),
            "tool",
            "run",
            *(["--offline"] if offline else []),
            "--python",
            self.PYTHON,
            "--from",
            self.REQUIREMENT,
            "tsdk",
            *tsdk_args,
        ]

    def play_command(self, cartridge: Path, args: List[str]) -> List[str]:
        """Return the command that plays a cartridge.

        Parameters
        ----------
        cartridge : Path
            The ``.ttea`` file.
        args : list[str]
            Session arguments (``--lang``, ``--player_id``,
            ``--professional_id`` and their values).

        Returns
        -------
        list[str]
            ``tsdk play`` run offline from the prepared environment,
            with ``--data-dir PathConfig.BASE_DIR`` so TSDK reads the
            platform calibration and saves the game data there. Run it
            with ``environment()``.
        """
        return self._command(
            True,
            "play",
            str(cartridge),
            *args,
            "--data-dir",
            str(PathConfig.BASE_DIR),
        )

    def prepare_command(self) -> List[str]:
        """Return the command that downloads and builds the environment.

        Returns
        -------
        list[str]
            ``tsdk --version`` run online; it exits with 0 once the
            environment is ready. Run it with ``environment()``.
        """
        return self._command(False, "--version")

    def is_ready(self) -> bool:
        """Check whether the environment is prepared.

        Returns
        -------
        bool
            True if ``tsdk --version`` runs offline from the
            environment.
        """
        creationflags = (
            subprocess.CREATE_NO_WINDOW
            if sys.platform.startswith("win")
            else 0
        )
        try:
            result = subprocess.run(
                self._command(True, "--version"),
                env=self.environment(),
                capture_output=True,
                timeout=60,
                creationflags=creationflags,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0
