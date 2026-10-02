import json
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from ttea.sdk.runtime import run_game
from ttea.sdk.simulator import SimulatorProvider
from ttea.sdk.tracking import Observation, Recording


CONSUMER = '''from ttea.sdk.api import Game
import pygame

class Consumer(Game):
    def start(self, context):
        self.events = ["start"]
        self.updates = []
        self.draws = []
    def update(self, context):
        self.events.append("update")
        self.updates.append(context.tracking.observation.timestamp)
    def draw(self, context):
        self.events.append("draw")
        self.draws.append(context.pause_reason)
        context.surface.fill((12, 34, 56))
        if context.config.get("keyboard"):
            key = pygame.K_p if len(self.draws) < 3 else pygame.K_ESCAPE
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    def pause(self, context):
        self.events.append("pause")
    def resume(self, context):
        self.events.append("resume")
    def stop(self, context):
        self.events.append("stop")
        return {"events": self.events, "updates": self.updates, "draws": self.draws}
'''


class RuntimeLifecycleTest(unittest.TestCase):
    def test_recorded_loss_staleness_and_recovery_across_profiles(self):
        for profile in ("body", "hands", "face"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "consumer.py").write_text(CONSUMER, encoding="utf-8")
                manifest = {"id": "test.lifecycle", "tracking_profile": profile,
                            "entrypoint": "consumer:Consumer"}
                recording = root / "tracking.jsonl"
                simulator = SimulatorProvider(profile)
                with Recording(recording, profile) as writer:
                    for timestamp in (10.0, 11.0, 12.0, 13.0, 14.0):
                        observation = simulator.read()
                        observation.timestamp = timestamp
                        if timestamp in (11.0, 12.0):
                            observation = Observation(profile, timestamp, {}, present=False)
                        elif timestamp == 13.0:
                            observation.timestamp = 10.0
                        writer.write(observation, now=timestamp)
                simulator.close()
                expected = {
                    "events": ["start", "update", "draw", "pause", "draw", "draw",
                               "draw", "resume", "update", "draw", "stop"],
                    "updates": [10.0, 14.0],
                    "draws": [None, "tracking_loss", "tracking_loss", "tracking_loss", None],
                }
                config = {"session_root": str(root / "sessions"), "fps": 0}
                for _ in range(2):
                    self.assertEqual(run_game(root, manifest, replay=recording, config=config), expected)
                results = list((root / "sessions" / "test.lifecycle" / "anonymous").glob("result-*.json"))
                self.assertEqual(len(results), 2)
                for path in results:
                    self.assertEqual(json.loads(path.read_text())["result"], expected)

    def test_keyboard_pause_resume_and_escape_use_runtime_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "consumer.py").write_text(CONSUMER, encoding="utf-8")
            manifest = {"id": "test.keyboard", "tracking_profile": "body",
                        "entrypoint": "consumer:Consumer"}
            result = run_game(root, manifest, simulation=True, max_frames=10,
                              config={"keyboard": True, "fps": 0,
                                      "session_root": str(root / "sessions")})
            self.assertEqual(result["events"], ["start", "update", "draw", "pause", "draw",
                                                "resume", "update", "draw", "stop"])
            self.assertEqual(result["draws"], [None, "user", None])


if __name__ == "__main__":
    unittest.main()
