import json
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ttea.controller.playergamelaunchcontroller import (
    PlayerGameLaunchController,
)
from ttea.model import GameMetadata
from ttea.service import PlayerGameLaunchService, TsdkService
from ttea.util import PathConfig

CONTROLLER = "ttea.controller.playergamelaunchcontroller"

MANIFEST = {
    "id": "br.udesc.test.cartridge",
    "version": "0.1.0",
    "entrypoint": "game.main:main",
    "tracking_profile": "tracking.toml",
    "game_api": "1",
    "requires_tsdk": ">=0.2,<0.3",
    "name": {"en": "Cartridge Game", "pt-BR": "Jogo Cartucho"},
    "description": "A test cartridge.",
    "assets": [],
    "licenses": ["LICENSE"],
    "format_version": 1,
    "builder": {"version": "0.2.0"},
    "build": {},
}

FOLDER_METADATA = {
    "schema_version": "1.0",
    "id": "br.udesc.test.folder",
    "version": "1.0.0",
    "runtime": {"entrypoint": "main.py"},
    "store": {
        "localization": {
            "default": "en_US",
            "en_US": {"name": "Folder Game"},
        }
    },
}


def write_cartridge(path: Path, manifest: dict) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
    return path


class CartridgeDiscoveryTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.games_dir = Path(tmp.name)

        folder = self.games_dir / "foldergame"
        folder.mkdir()
        (folder / "metadata.json").write_text(json.dumps(FOLDER_METADATA))

        for patcher in (
            patch.object(PathConfig, "EXERGAME_DIR", self.games_dir),
            patch("ttea.service.PlayerService"),
            patch("ttea.service.ProfessionalService"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

        patcher = patch("ttea.log.Log.get_log")
        self.log = patcher.start().return_value
        self.addCleanup(patcher.stop)

    def games(self):
        service = PlayerGameLaunchService()
        return {g.id: g for g in service.get_games_metadata()}

    def test_valid_cartridge_loads_alongside_folder_game(self):
        write_cartridge(self.games_dir / "game.ttea", MANIFEST)

        games = self.games()

        self.assertEqual(
            set(games), {"br.udesc.test.folder", "br.udesc.test.cartridge"}
        )
        self.assertEqual(
            games["br.udesc.test.folder"].name("en_US"), "Folder Game"
        )

        cartridge = games["br.udesc.test.cartridge"]
        self.assertEqual(cartridge.version, "0.1.0")
        self.assertEqual(cartridge.entrypoint, "game.ttea")
        self.assertEqual(
            cartridge.entrypoint_path, self.games_dir / "game.ttea"
        )
        self.assertIsNone(cartridge.view_factory)
        self.assertEqual(cartridge.menu_actions, {})
        self.assertEqual(cartridge.name("en_US"), "Cartridge Game")
        self.assertEqual(cartridge.name("pt_BR"), "Jogo Cartucho")
        self.assertEqual(cartridge.name("es_ES"), "Cartridge Game")
        self.assertEqual(
            cartridge.text("pt_BR", "short_description"), "A test cartridge."
        )
        self.log.log_warning.assert_not_called()

    def test_corrupt_cartridges_are_skipped(self):
        (self.games_dir / "broken.ttea").write_bytes(b"not a zip")
        with zipfile.ZipFile(self.games_dir / "empty.ttea", "w") as zf:
            zf.writestr("readme.txt", "no manifest")
        write_cartridge(
            self.games_dir / "nameless.ttea",
            {k: v for k, v in MANIFEST.items() if k != "name"},
        )
        stored = write_cartridge(self.games_dir / "aes.ttea", MANIFEST)
        data = bytearray(stored.read_bytes())
        for signature, offset in ((b"PK\x03\x04", 8), (b"PK\x01\x02", 10)):
            at = data.index(signature) + offset
            data[at : at + 2] = (99).to_bytes(2, "little")
        stored.write_bytes(bytes(data))
        write_cartridge(
            self.games_dir / "future.ttea", {**MANIFEST, "format_version": 2}
        )

        self.assertEqual(set(self.games()), {"br.udesc.test.folder"})
        self.assertEqual(self.log.log_warning.call_count, 5)

    def test_folder_game_wins_over_cartridge_with_same_id(self):
        write_cartridge(
            self.games_dir / "a.ttea",
            {**MANIFEST, "id": FOLDER_METADATA["id"]},
        )

        games = self.games()

        self.assertEqual(list(games), ["br.udesc.test.folder"])
        self.assertEqual(games["br.udesc.test.folder"].entrypoint, "main.py")
        self.log.log_warning.assert_called_once()


class CartridgeLaunchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QApplication.instance() or QApplication([])

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cartridge_path = write_cartridge(
            Path(tmp.name) / "game.ttea", MANIFEST
        )
        self.game = GameMetadata.load_cartridge(self.cartridge_path)

        view = MagicMock()
        view.cbx_game.currentData.return_value = self.game
        view.cbx_player.currentData.return_value = 7
        view.cbx_professional.currentData.return_value = 3
        calibration = MagicMock()
        calibration.get_camera_info.return_value = None
        calibration.get_screen_info.return_value = None
        self.msg = MagicMock()
        self.tsdk = TsdkService()
        self.controller = PlayerGameLaunchController(
            view,
            message_service=self.msg,
            service=MagicMock(),
            calibration_service=calibration,
            tsdk_service=self.tsdk,
        )
        self.addCleanup(self.controller.cleanup)

        patcher = patch.object(
            TsdkService, "uv_executable", return_value="/bin/uv"
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(f"{CONTROLLER}.QProgressDialog")
        dialog = patcher.start().return_value
        dialog.wasCanceled.return_value = False
        self.addCleanup(patcher.stop)
        patcher = patch(f"{CONTROLLER}.AppModel")
        patcher.start().get_instance.return_value.current_language = "es_ES"
        self.addCleanup(patcher.stop)
        patcher = patch(f"{CONTROLLER}.subprocess.Popen")
        self.popen = patcher.start()
        self.popen.return_value.poll.return_value = 0
        self.addCleanup(patcher.stop)

    def launch(self, ready, prepare=None, answer=True):
        """Launch the cartridge and wait for any runtime preparation."""
        self.msg.question.return_value = answer
        with (
            patch.object(self.tsdk, "is_ready", return_value=ready),
            patch.object(self.tsdk, "prepare_command", return_value=prepare),
        ):
            self.controller.launch_game()
            deadline = time.monotonic() + 30
            while (
                self.controller.prepare_process is not None
                and time.monotonic() < deadline
            ):
                self.qt_app.processEvents()
                time.sleep(0.01)

    def assert_played(self):
        self.popen.assert_called_once()
        args, kwargs = self.popen.call_args
        self.assertEqual(
            args[0],
            [
                "/bin/uv",
                "tool",
                "run",
                "--offline",
                "--python",
                TsdkService.PYTHON,
                "--from",
                TsdkService.REQUIREMENT,
                "tsdk",
                "play",
                str(self.cartridge_path),
                "--lang",
                "es_ES",
                "--player_id",
                "7",
                "--professional_id",
                "3",
                "--data-dir",
                str(PathConfig.BASE_DIR),
            ],
        )
        self.assertEqual(kwargs["cwd"], str(self.cartridge_path.parent))
        runtime = PathConfig.RUNTIME_DIR
        env = kwargs["env"]
        self.assertEqual(env["UV_CACHE_DIR"], str(runtime / "cache"))
        self.assertEqual(env["UV_PYTHON_INSTALL_DIR"], str(runtime / "python"))
        self.assertEqual(env["UV_PYTHON_PREFERENCE"], "only-managed")

    def test_prepared_runtime_plays_cartridge_offline(self):
        self.launch(ready=True)

        self.assert_played()
        self.msg.question.assert_not_called()

    def test_declined_preparation_does_not_launch(self):
        self.launch(ready=False, answer=False)

        self.msg.question.assert_called_once()
        self.popen.assert_not_called()

    def test_successful_preparation_then_plays(self):
        self.launch(ready=False, prepare=[sys.executable, "-c", "pass"])

        self.assert_played()
        self.msg.critical.assert_not_called()

    def test_failed_preparation_shows_uv_output(self):
        script = "print('no network'); raise SystemExit(2)"
        self.launch(ready=False, prepare=[sys.executable, "-c", script])

        self.popen.assert_not_called()
        self.msg.critical.assert_called_once()
        self.assertIn("no network", self.msg.critical.call_args[0][0])

    def test_missing_uv_is_reported(self):
        self.launch(ready=False, prepare=["/nonexistent/uv", "--version"])

        self.popen.assert_not_called()
        self.msg.critical.assert_called_once()

    def test_closing_during_preparation_stops_it_without_playing(self):
        self.msg.question.return_value = True
        slow = [sys.executable, "-c", "import time; time.sleep(30)"]
        with (
            patch.object(self.tsdk, "is_ready", return_value=False),
            patch.object(self.tsdk, "prepare_command", return_value=slow),
        ):
            self.controller.launch_game()
            process = self.controller.prepare_process
            self.assertTrue(process.waitForStarted(5000))
            self.controller.cleanup()
            for _ in range(20):
                self.qt_app.processEvents()
                time.sleep(0.01)

        self.assertIsNone(self.controller.prepare_process)
        self.assertEqual(process.state(), process.ProcessState.NotRunning)
        self.popen.assert_not_called()
        self.msg.critical.assert_not_called()

    def test_python_games_keep_their_command(self):
        game = GameMetadata(
            id="py",
            version="1",
            folder_path=Path("/games/py"),
            entrypoint="main.py",
            view_factory=None,
            menu_actions={},
            icon=None,
            developers=[],
            release_date=None,
            required_peripherals=[],
            localization={},
            default_language="en_US",
        )
        self.assertEqual(
            self.controller.build_game_command(game, "pt_BR", "1", "2"),
            [
                sys.executable,
                str(Path("/games/py/main.py")),
                "--lang",
                "pt_BR",
                "--player_id",
                "1",
                "--professional_id",
                "2",
            ],
        )


if __name__ == "__main__":
    unittest.main()
