"""Snapshot module: capture and compare env state at a point in time."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class EnvSnapshot:
    """Immutable snapshot of parsed env key/value pairs with metadata."""

    source: str
    captured_at: str
    data: Dict[str, str]
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        payload = json.dumps(self.data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:16]

    def diff_keys(self, other: "EnvSnapshot") -> Dict[str, Optional[str]]:
        """Return keys present in self but missing or different in other."""
        result: Dict[str, Optional[str]] = {}
        for key, value in self.data.items():
            if key not in other.data:
                result[key] = None
            elif other.data[key] != value:
                result[key] = other.data[key]
        return result

    def is_identical(self, other: "EnvSnapshot") -> bool:
        return self.checksum == other.checksum

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "captured_at": self.captured_at,
            "checksum": self.checksum,
            "data": self.data,
        }


class SnapshotManager:
    """Create and persist env snapshots to disk."""

    def __init__(self, snapshot_dir: Path) -> None:
        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, source: str, data: Dict[str, str]) -> EnvSnapshot:
        ts = datetime.now(timezone.utc).isoformat()
        return EnvSnapshot(source=source, captured_at=ts, data=data)

    def save(self, snapshot: EnvSnapshot) -> Path:
        safe_name = snapshot.source.replace("/", "_").replace(".", "_")
        filename = f"{safe_name}_{snapshot.checksum}.json"
        path = self.snapshot_dir / filename
        path.write_text(json.dumps(snapshot.to_dict(), indent=2))
        return path

    def load(self, path: Path) -> EnvSnapshot:
        raw = json.loads(path.read_text())
        return EnvSnapshot(
            source=raw["source"],
            captured_at=raw["captured_at"],
            data=raw["data"],
        )

    def list_snapshots(self) -> list[Path]:
        return sorted(self.snapshot_dir.glob("*.json"))
