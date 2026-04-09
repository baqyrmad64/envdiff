"""Watch .env files for changes and trigger re-comparison."""

import time
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class FileSnapshot:
    path: str
    mtime: float
    size: int

    @classmethod
    def from_path(cls, path: str) -> "FileSnapshot":
        stat = os.stat(path)
        return cls(path=path, mtime=stat.st_mtime, size=stat.st_size)

    def has_changed(self) -> bool:
        try:
            current = os.stat(self.path)
            return current.st_mtime != self.mtime or current.st_size != self.size
        except FileNotFoundError:
            return True


@dataclass
class WatchEvent:
    changed_files: List[str]
    timestamp: float = field(default_factory=time.time)


class EnvWatcher:
    def __init__(self, paths: List[str], interval: float = 1.0):
        self.paths = paths
        self.interval = interval
        self._snapshots: Dict[str, FileSnapshot] = {}
        self._running = False
        self._on_change: Optional[Callable[[WatchEvent], None]] = None

    def on_change(self, callback: Callable[[WatchEvent], None]) -> None:
        self._on_change = callback

    def _take_snapshots(self) -> None:
        for path in self.paths:
            if os.path.exists(path):
                self._snapshots[path] = FileSnapshot.from_path(path)

    def _detect_changes(self) -> List[str]:
        changed = []
        for path, snapshot in self._snapshots.items():
            if snapshot.has_changed():
                changed.append(path)
        for path in self.paths:
            if path not in self._snapshots and os.path.exists(path):
                changed.append(path)
        return changed

    def start(self, max_iterations: Optional[int] = None) -> None:
        self._running = True
        self._take_snapshots()
        iterations = 0
        while self._running:
            time.sleep(self.interval)
            changed = self._detect_changes()
            if changed:
                self._take_snapshots()
                if self._on_change:
                    self._on_change(WatchEvent(changed_files=changed))
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break

    def stop(self) -> None:
        self._running = False
