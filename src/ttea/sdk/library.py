"""Reviewed cartridge catalog and offline installation lifecycle."""

import hashlib
from contextlib import contextmanager
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from importlib.metadata import version
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from platformdirs import user_data_dir

from ttea.sdk.cartridge import extract_cartridge, inspect_cartridge

MAX_DOWNLOAD = 512 * 1024 * 1024

logger = logging.getLogger(__name__)


def catalog():
    return json.loads(Path(__file__).with_name("catalog.json").read_text(encoding="utf-8"))["games"]


def localized(texts, language, default=None):
    """Pick a manifest text: exact BCP 47 tag, then its language subtag, then the first entry."""
    if not texts:
        return default
    tag = str(language or "").replace("_", "-")
    lowered = {key.lower(): value for key, value in texts.items()}
    for candidate in (tag.lower(), tag.split("-")[0].lower()):
        if candidate in lowered:
            return lowered[candidate]
    return next(iter(texts.values()))


def resolve_release(game, runtime_version=None):
    """Select only reviewed stable releases compatible with this platform."""
    current = Version(runtime_version or version("t-tea"))
    compatible = []
    for release in game.get("releases", []):
        candidate = Version(release["version"])
        if candidate.is_prerelease or candidate.is_devrelease or release.get("draft", False):
            continue
        if release.get("game_api") != 1 or release.get("format_version") != 1:
            continue
        if current not in SpecifierSet(release["requires_ttea"]):
            continue
        compatible.append(release)
    return max(compatible, key=lambda item: Version(item["version"]), default=None)


def _fsync_directory(path):
    """Persist a rename on POSIX; Windows cannot open directories for fsync."""
    if sys.platform == "win32":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class Library:
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else Path(user_data_dir("ttea", "udesc")) / "library"
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "receipts").mkdir(exist_ok=True)
        (self.root / "versions").mkdir(exist_ok=True)

    def _receipt_path(self, game_id):
        if not isinstance(game_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", game_id):
            raise ValueError("Invalid game identity")
        return self.root / "receipts" / (game_id + ".json")

    @contextmanager
    def _operation(self, game_id):
        lock_path = self._receipt_path(game_id).with_suffix(".lock")
        with lock_path.open("a+b") as lock:
            if sys.platform == "win32":
                import msvcrt
                if lock.seek(0, os.SEEK_END) == 0:
                    lock.write(b"\0")
                    lock.flush()
                lock.seek(0)
                try:
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise ValueError("Conflicting library operation") from exc
                try:
                    yield
                finally:
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise ValueError("Conflicting library operation") from exc
                try:
                    yield
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def receipt(self, game_id):
        path = self._receipt_path(game_id)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def installed(self):
        """List parseable receipts; a corrupt receipt is logged and left in place for recovery."""
        receipts = []
        for path in sorted((self.root / "receipts").glob("*.json")):
            try:
                receipts.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                logger.warning("Skipping unreadable TSDK receipt %s", path, exc_info=True)
        return receipts

    def install(self, url, sha256, *, expected_id=None, expected_version=None, update=False):
        """Download and verify before atomically switching the active receipt."""
        if not re.fullmatch(r"[a-fA-F0-9]{64}", sha256):
            raise ValueError("A SHA-256 digest is required")
        parsed = urlparse(url)
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}):
            raise ValueError("Downloads require HTTPS (HTTP is allowed only on loopback)")
        with tempfile.TemporaryDirectory(prefix="staging-", dir=self.root) as staging:
            staging = Path(staging)
            archive = staging / "download.ttea"
            digest = hashlib.sha256()
            size = 0
            request = Request(url, headers={"User-Agent": "TTEA-TTEA-Library/1"})
            with urlopen(request, timeout=30) as response, archive.open("wb") as output:
                redirected = urlparse(response.url)
                if redirected.scheme != "https" and not (redirected.scheme == "http" and redirected.hostname in {"127.0.0.1", "localhost", "::1"}):
                    raise ValueError("Unsafe download redirect")
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_DOWNLOAD:
                        raise ValueError("Cartridge download exceeds size limit")
                    digest.update(chunk)
                    output.write(chunk)
            if digest.hexdigest() != sha256.lower():
                raise ValueError("Cartridge SHA-256 mismatch")
            manifest = inspect_cartridge(archive)
            game_id = manifest["id"]
            receipt_path = self._receipt_path(game_id)
            if expected_id is not None and game_id != expected_id:
                raise ValueError("Cartridge identity does not match catalog")
            if expected_version is not None and manifest["version"] != expected_version:
                raise ValueError("Cartridge version does not match catalog")
            with self._operation(game_id):
                previous = self.receipt(game_id)
                if previous and not update:
                    raise ValueError("Game already installed; request an explicit update")
                if previous and Version(manifest["version"]) <= Version(previous["manifest"]["version"]):
                    raise ValueError("Update must be newer than the installed version")
                extracted = staging / "game"
                extract_cartridge(archive, extracted)
                directory = uuid4().hex
                destination = self.root / "versions" / directory
                receipt = {"manifest": manifest, "directory": directory, "url": url,
                           "sha256": sha256.lower(), "installed_at": datetime.now(timezone.utc).isoformat()}
                receipt["history"] = (
                    previous.get("history", []) + [{key: value for key, value in previous.items() if key != "history"}]
                    if previous else []
                )
                staged_receipt = staging / "receipt.json"
                with staged_receipt.open("w", encoding="utf-8") as handle:
                    handle.write(json.dumps(receipt, ensure_ascii=False, indent=2))
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(extracted, destination)
                try:
                    os.replace(staged_receipt, receipt_path)
                    _fsync_directory(receipt_path.parent)
                except BaseException:
                    shutil.rmtree(destination)
                    raise
                return receipt

    def install_release(self, game, *, update=False):
        release = resolve_release(game)
        if release is None:
            raise ValueError("No reviewed compatible stable cartridge is published")
        return self.install(release["url"], release["sha256"], expected_id=game["id"],
                            expected_version=release["version"], update=update)

    def launch(self, game_id, *, simulation=False, replay=None, max_frames=None, config=None):
        receipt = self.receipt(game_id)
        if receipt is None:
            raise ValueError("Game is not installed")
        directory = receipt["directory"]
        if not re.fullmatch(r"[a-f0-9]{32}", directory):
            raise ValueError("Invalid installation receipt")
        project = self.root / "versions" / directory
        if not project.is_dir():
            raise ValueError("Installed cartridge is missing")
        return self.launch_project(project, simulation=simulation, replay=replay, max_frames=max_frames, config=config)

    @staticmethod
    def launch_project(project, *, simulation=False, replay=None, max_frames=None, config=None):
        project = Path(project)
        command = [sys.executable, "-m", "ttea.sdk.runtime", str(project.resolve())]
        if simulation:
            command.append("--simulation")
        if replay is not None:
            command.extend(["--replay", str(Path(replay).resolve())])
        if max_frames is not None:
            command.extend(["--max-frames", str(max_frames)])
        if config is not None:
            command.extend(["--config", json.dumps(config)])
        return subprocess.Popen(command, cwd=project, creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0))

    def uninstall(self, game_id):
        with self._operation(game_id):
            receipt = self.receipt(game_id)
            if receipt is None:
                return
            directories = [receipt["directory"]] + [item["directory"] for item in receipt.get("history", [])]
            if any(not re.fullmatch(r"[a-f0-9]{32}", directory) for directory in directories):
                raise ValueError("Invalid installation receipt")
            self._receipt_path(game_id).unlink()
            for directory in directories:
                shutil.rmtree(self.root / "versions" / directory, ignore_errors=True)
            # Runtime session storage is outside the code installation tree.
