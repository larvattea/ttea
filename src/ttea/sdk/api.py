"""Version-one game lifecycle and game-scoped persistent JSON storage."""
from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from platformdirs import user_data_dir

if TYPE_CHECKING:
    import pygame
    from .tracking import TrackingFrame


def _component(value: str) -> str:
    if not value or value in {".", ".."} or any(c in value for c in '/\\\x00'):
        raise ValueError("Storage names must be single path components")
    return value


class SessionStorage:
    """JSON saves and immutable result records, independent of installed code."""

    def __init__(self, game_id: str, player_id: str = "anonymous", root: Path | None = None) -> None:
        base = Path(root) if root is not None else Path(user_data_dir("ttea", "udesc")) / "tsdk" / "sessions"
        self.root = base / _component(game_id) / _component(str(player_id))
        self.root.mkdir(parents=True, exist_ok=True)

    def read(self, name: str, default: Any = None) -> Any:
        path = self.root / (_component(name) + ".json")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return default

    def write(self, name: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False, allow_nan=False)
        destination = self.root / (_component(name) + ".json")
        descriptor, temporary = tempfile.mkstemp(prefix=".save-", dir=self.root)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def record_result(self, result: dict) -> Path:
        name = "result-" + uuid.uuid4().hex
        self.write(name, {"recorded_at": datetime.now(timezone.utc).isoformat(), "result": result})
        return self.root / (name + ".json")


@dataclass
class GameContext:
    surface: pygame.Surface
    tracking: TrackingFrame
    dt: float
    elapsed: float
    events: tuple[pygame.event.Event, ...]
    assets: Path
    config: dict
    storage: SessionStorage
    paused: bool = False
    pause_reason: str | None = None
    stop_requested: bool = False
    result: dict | None = field(default=None, repr=False)

    def request_stop(self, result: dict | None = None) -> None:
        self.stop_requested = True
        if result is not None:
            self.result = result


class Game:
    """Subclass and override callbacks; the platform owns the event loop."""

    def start(self, context: GameContext) -> None:
        pass

    def update(self, context: GameContext) -> None:
        pass

    def draw(self, context: GameContext) -> None:
        pass

    def pause(self, context: GameContext) -> None:
        pass

    def resume(self, context: GameContext) -> None:
        pass

    def stop(self, context: GameContext) -> dict | None:
        return None
