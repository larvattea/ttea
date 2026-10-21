import json
import os
import sys
import tempfile
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
from ttea.service import PlayerGameLaunchService
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

        self.assertEqual(set(self.games()), {"br.udesc.test.folder"})
        self.assertEqual(self.log.log_warning.call_count, 4)

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
        self.calibration = calibration
        self.controller = PlayerGameLaunchController(
            view,
            message_service=self.msg,
            service=MagicMock(),
            calibration_service=calibration,
        )
        self.addCleanup(self.controller.cleanup)

        patcher = patch(f"{CONTROLLER}.AppModel")
        patcher.start().get_instance.return_value.current_language = "es_ES"
        self.addCleanup(patcher.stop)

    def expected_command(self, tsdk):
        return [
            tsdk,
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
        ]

    def test_cartridge_launches_through_tsdk(self):
        tsdk = "/opt/bin/tsdk"
        with patch("shutil.which", return_value=tsdk) as which:
            self.assertEqual(
                PlayerGameLaunchController.build_game_command(
                    self.game, "es_ES", "7", "3"
                ),
                self.expected_command(tsdk),
            )
            which.assert_called_once_with("tsdk")

            with patch(f"{CONTROLLER}.subprocess.Popen") as popen:
                popen.return_value.poll.return_value = 0
                self.controller.launch_game()

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], self.expected_command(tsdk))
        self.assertEqual(kwargs["cwd"], str(self.cartridge_path.parent))
        self.msg.warning.assert_not_called()

    def test_missing_tsdk_does_not_launch(self):
        with (
            patch("shutil.which", return_value=None),
            patch(f"{CONTROLLER}.subprocess.Popen") as popen,
        ):
            self.assertIsNone(
                PlayerGameLaunchController.build_game_command(
                    self.game, "es_ES", "7", "3"
                )
            )
            self.controller.launch_game()

        popen.assert_not_called()
        self.msg.warning.assert_called_once()
        self.calibration.find_by_id_calibration_point.assert_not_called()

    def test_tsdk_found_in_uv_tool_dir_off_path(self):
        uv_bin = str(Path.home() / ".local" / "bin")
        tsdk = os.path.join(uv_bin, "tsdk")

        def which(name, path=None):
            return tsdk if path == uv_bin else None

        with patch("shutil.which", side_effect=which):
            self.assertEqual(
                PlayerGameLaunchController.build_game_command(
                    self.game, "es_ES", "7", "3"
                ),
                self.expected_command(tsdk),
            )

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
            PlayerGameLaunchController.build_game_command(
                game, "pt_BR", "1", "2"
            ),
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
