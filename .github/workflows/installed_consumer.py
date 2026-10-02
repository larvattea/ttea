"""Run from outside the checkout against an installed TTEA wheel.

Optionally pass an independently built game cartridge to exercise its lifecycle.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

from ttea.sdk.cartridge import extract_cartridge
from ttea.sdk.runtime import run_game

game_archive = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    os.chdir(root)
    manifest = {
        "id": "ci.consumer", "version": "1.0.0", "entrypoint": "consumer:Consumer",
        "tracking_profile": "body", "game_api": 1, "requires_ttea": ">=2.0,<3",
        "name": {"en": "Independent CI consumer"}, "assets": [], "licenses": ["NOTICE"],
        "format_version": 1, "builder": {"version": "0.0.0"},
        "build": {"source_commit": "unversioned", "dirty": True},
    }
    source = '''from ttea.sdk.api import Game

class Consumer(Game):
    def start(self, context):
        self.frames = 0
        self.positions = []
    def update(self, context):
        assert not context.tracking.missing
        self.positions.append(context.tracking.feet["left"].x)
        self.frames += 1
        if self.frames == 3:
            context.request_stop()
    def draw(self, context):
        context.surface.fill((12, 34, 56))
    def stop(self, context):
        result = {"frames": self.frames, "positions": self.positions}
        context.storage.write("consumer.json", result)
        return result
'''
    artifact = root / "consumer.ttea"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("consumer.py", source)
        archive.writestr("NOTICE", "CI-only synthetic cartridge fixture; not a published release.\n")
    installed = root / "installed"
    metadata = extract_cartridge(artifact, installed)
    result = run_game(installed, metadata, simulation=True, max_frames=10,
                      config={"session_root": str(root / "sessions")})
    assert result["frames"] == 3, result
    assert all(0 <= x <= 1 for x in result["positions"]), result
    print("Independent installed cartridge:", result)

    if game_archive is not None:
        project = root / "game"
        metadata = extract_cartridge(game_archive, project)
        result = run_game(project, metadata, simulation=True, max_frames=5,
                          config={"autostart": True, "session_root": str(root / "sessions")})
        print("Installed independent game:", metadata["id"], result)
    os.chdir(Path(directory).parent)
