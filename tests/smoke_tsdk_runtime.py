"""End-to-end smoke of ``.ttea`` games on the real TSDK runtime.

Not run by ``uv run tests``: it downloads TSDK (about 2 GB) on first
use. CI runs it on Windows; run it anywhere with::

    uv run python tests/smoke_tsdk_runtime.py [BASE_DIR]

``BASE_DIR`` is the T-TEA data folder to use, and it must not exist or
be empty: the script writes a calibration there. Default: a temporary
folder. CI passes the data folder of the packaged build
(``%LOCALAPPDATA%\\udesc\\ttea`` on Windows), so path lengths match a
real installation. Steps:

1. The launch screen controller prepares TSDK through the real
   ``QProcess`` and progress dialog, then starts the cartridge.
2. With the network unreachable, TSDK is still ready and ``tsdk play``
   gets through cartridge validation and the platform calibration up to
   the camera (on a machine without a camera, it must fail there).
3. In the TSDK environment, MediaPipe pose tracking runs on a frame
   and the cartridge's game runs in simulation.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import psutil
from PySide6.QtWidgets import QApplication, QDialog

from ttea.util import PathConfig

FIXTURE = Path(__file__).with_name("fixtures") / "smoke-0.1.0.ttea"
DEAD_PROXY = "http://127.0.0.1:9"

SIMULATION = """
import sys, tempfile
from pathlib import Path
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from tsdk.cartridge import extract_cartridge
from tsdk.providers import MODELS
from tsdk.runtime import run_game

options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(
        model_asset_path=str(MODELS / "pose_landmarker_full.task")
    ),
    running_mode=vision.RunningMode.VIDEO,
)
with vision.PoseLandmarker.create_from_options(options) as detector:
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    result = detector.detect_for_video(image, 0)
print("tracking: poses on a blank frame =", len(result.pose_landmarks))

with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "game"
    manifest = extract_cartridge(Path(sys.argv[1]), project)
    config = {"session_root": str(Path(tmp) / "sessions"), "autostart": True}
    print("simulation:", run_game(project, manifest, simulation=True,
                                  max_frames=30, config=config))
"""


def check(condition, message):
    if not condition:
        raise SystemExit(f"FAILED: {message}")
    print(f"ok: {message}")


def pump(app, seconds, until):
    end = time.monotonic() + seconds
    while time.monotonic() < end and not until():
        app.processEvents()
        time.sleep(0.05)


def save_calibration(app):
    from ttea.service import CalibrationService

    screen = app.screens()[0].geometry()
    service = CalibrationService()
    service.create_calibration_hardware({
        "camera_description": "smoke", "camera_id": "smoke",
        "camera_position": 0, "camera_width": 640, "camera_height": 480,
        "camera_max_fps": 30, "camera_min_fps": 1,
        "screen_manufacturer": "", "screen_model": "",
        "screen_position": 0, "screen_serial_number": "",
        "screen_width": screen.width(), "screen_height": screen.height(),
        "screen_available_width": screen.width(),
        "screen_available_height": screen.height(),
        "screen_pos_x": 0, "screen_pos_y": 0,
        "content_width": screen.width(), "content_height": screen.height(),
        "content_width_ratio": 4, "content_height_ratio": 3,
        "content_proportion": "4:3",
        "calibration_date": "2026-01-01", "calibration_hour": "00:00:00",
    })
    service.create_calibration_point({
        "pointx1": 100, "pointy1": 100, "pointx2": 540, "pointy2": 100,
        "pointx3": 100, "pointy3": 380, "pointx4": 540, "pointy4": 380,
    })


def launch_from_controller(app, game):
    """Step 1: prepare TSDK and start the game from the launch screen."""
    from ttea.controller.playergamelaunchcontroller import (
        PlayerGameLaunchController,
    )

    view = QDialog()
    view.cbx_game = MagicMock()
    view.cbx_game.currentData.return_value = game
    view.cbx_player = MagicMock()
    view.cbx_player.currentData.return_value = 7
    view.cbx_professional = MagicMock()
    view.cbx_professional.currentData.return_value = 3
    view.pb_play = MagicMock()
    view.pb_cancel = MagicMock()
    msg = MagicMock()
    msg.question.return_value = True
    controller = PlayerGameLaunchController(view, message_service=msg)

    started = time.monotonic()
    controller.launch_game()
    texts = [call.args[0] for call in msg.question.call_args_list]
    check(any("TSDK" in text for text in texts), "asked before downloading")
    pump(app, 1800, lambda: controller.prepare_process is None)
    print(f"prepared in {time.monotonic() - started:.0f} s")
    check(not msg.critical.called, f"no error shown: {msg.critical.call_args}")
    check(controller.current_process is not None, "game process started")
    pump(app, 30, lambda: controller.current_process.poll() is not None)
    print("game return code after start:", controller.current_process.poll())
    controller.cleanup()


def play_offline(tsdk, game):
    """Step 2: ``tsdk play`` with the network unreachable."""
    os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = DEAD_PROXY
    check(tsdk.is_ready(), "TSDK ready with the network unreachable")
    process = subprocess.Popen(
        tsdk.play_command(
            game.entrypoint_path,
            ["--lang", "pt_BR", "--player_id", "7", "--professional_id", "3"],
        ),
        cwd=game.folder_path,
        env=tsdk.environment(),
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    try:
        _, stderr = process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        # uv runs tsdk as its child; killing only uv would orphan the
        # game, which keeps the stderr pipe open
        parent = psutil.Process(process.pid)
        for proc in [*parent.children(recursive=True), parent]:
            proc.kill()
        process.communicate()
        print("ok: tsdk play offline kept running (camera present)")
        return
    print(stderr.strip()[-600:])
    check(
        "camera" in stderr.lower(),
        "tsdk play offline reached the camera (none on this machine)",
    )


def simulate(tsdk, game):
    """Step 3: tracking and the game itself in the TSDK environment."""
    result = subprocess.run(
        [
            tsdk.uv_executable(), "tool", "run", "--offline",
            "--python", tsdk.PYTHON, "--from", tsdk.REQUIREMENT,
            "python", "-c", SIMULATION, str(game.entrypoint_path),
        ],
        env=tsdk.environment(),
        capture_output=True,
        text=True,
        errors="replace",
        timeout=600,
    )
    print(result.stdout.strip()[-1500:], result.stderr.strip()[-1500:])
    check(result.returncode == 0, "tracking and simulated game run in TSDK")


def main(base):
    if base.exists() and any(base.iterdir()):
        raise SystemExit(f"Refusing to use a non-empty data folder: {base}")
    app = QApplication([])
    PathConfig.set_base_dir(base)
    PathConfig.ensure_dirs()
    PathConfig.EXERGAME_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURE, PathConfig.EXERGAME_DIR / FIXTURE.name)
    print("data dir:", base, "| platform:", sys.platform)

    from ttea.model import AppModel
    from ttea.service import PlayerGameLaunchService, TsdkService

    save_calibration(app)
    AppModel.get_instance().current_language = "pt_BR"
    games = PlayerGameLaunchService().get_games_metadata()
    game = next(g for g in games if g.is_cartridge)
    check(game.id == "smoke", "cartridge listed on the launch screen")

    tsdk = TsdkService()
    print("uv:", tsdk.uv_executable())
    check(not tsdk.is_ready(), "TSDK not prepared yet")
    launch_from_controller(app, game)
    play_offline(tsdk, game)
    simulate(tsdk, game)
    print("SMOKE PASSED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(Path(sys.argv[1]))
    else:
        with tempfile.TemporaryDirectory(prefix="ttea-smoke-") as tmp:
            main(Path(tmp))
