"""Audit trail for env diff operations — tracks what was compared, when, and what changed."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envdiff.comparator import ComparisonResult


@dataclass
class AuditEntry:
    timestamp: str
    base_env: str
    target_env: str
    missing_keys: List[str]
    extra_keys: List[str]
    mismatched_keys: List[str]
    total_issues: int
    note: Optional[str] = None

    @classmethod
    def from_result(cls, result: ComparisonResult, base_name: str, target_name: str, note: Optional[str] = None) -> "AuditEntry":
        issues = len(result.missing_keys) + len(result.extra_keys) + len(result.mismatched_keys)
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            base_env=base_name,
            target_env=target_name,
            missing_keys=list(result.missing_keys),
            extra_keys=list(result.extra_keys),
            mismatched_keys=list(result.mismatched_keys),
            total_issues=issues,
            note=note,
        )

    def is_clean(self) -> bool:
        return self.total_issues == 0

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "base_env": self.base_env,
            "target_env": self.target_env,
            "missing_keys": self.missing_keys,
            "extra_keys": self.extra_keys,
            "mismatched_keys": self.mismatched_keys,
            "total_issues": self.total_issues,
            "note": self.note,
        }


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def record(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def clean_runs(self) -> List[AuditEntry]:
        return [e for e in self.entries if e.is_clean()]

    def dirty_runs(self) -> List[AuditEntry]:
        return [e for e in self.entries if not e.is_clean()]

    def summary(self) -> dict:
        return {
            "total_runs": len(self.entries),
            "clean_runs": len(self.clean_runs()),
            "dirty_runs": len(self.dirty_runs()),
        }

    def to_dict(self) -> dict:
        return {
            "summary": self.summary(),
            "entries": [e.to_dict() for e in self.entries],
        }
