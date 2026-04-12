"""Baseline management: save and compare env state against a stored baseline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass
class BaselineEntry:
    key: str
    value: str

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> "BaselineEntry":
        return cls(key=d["key"], value=d["value"])


@dataclass
class BaselineDiff:
    added: List[str] = field(default_factory=list)      # keys new since baseline
    removed: List[str] = field(default_factory=list)    # keys gone since baseline
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def is_clean(self) -> bool:
        return not self.added and not self.removed and not self.changed

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


@dataclass
class Baseline:
    source: str
    entries: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "entries": self.entries,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Baseline":
        return cls(source=d["source"], entries=d.get("entries", {}))


class BaselineManager:
    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path

    def save(self, baseline: Baseline) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {}
        if self.store_path.exists():
            data = json.loads(self.store_path.read_text())
        data[baseline.source] = baseline.to_dict()
        self.store_path.write_text(json.dumps(data, indent=2))

    def load(self, source: str) -> Optional[Baseline]:
        if not self.store_path.exists():
            return None
        data = json.loads(self.store_path.read_text())
        if source not in data:
            return None
        return Baseline.from_dict(data[source])

    def compare(self, source: str, current: Dict[str, str]) -> Optional[BaselineDiff]:
        baseline = self.load(source)
        if baseline is None:
            return None
        diff = BaselineDiff()
        old = baseline.entries
        diff.added = [k for k in current if k not in old]
        diff.removed = [k for k in old if k not in current]
        diff.changed = {
            k: (old[k], current[k])
            for k in current
            if k in old and old[k] != current[k]
        }
        return diff
