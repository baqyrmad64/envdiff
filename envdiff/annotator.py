"""Annotate env keys with metadata: source file, line number, and raw line."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AnnotatedKey:
    key: str
    value: str
    source: str
    line_number: int
    raw_line: str
    comment: Optional[str] = None

    def has_comment(self) -> bool:
        return self.comment is not None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "line_number": self.line_number,
            "raw_line": self.raw_line,
            "comment": self.comment,
        }


@dataclass
class AnnotationResult:
    source: str
    entries: List[AnnotatedKey] = field(default_factory=list)

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def get(self, key: str) -> Optional[AnnotatedKey]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def with_comments(self) -> List[AnnotatedKey]:
        return [e for e in self.entries if e.has_comment()]


class EnvAnnotator:
    """Parse a .env file and return annotated key metadata."""

    def annotate(self, path: Path) -> AnnotationResult:
        source = str(path)
        result = AnnotationResult(source=source)
        if not path.exists():
            return result

        lines = path.read_text(encoding="utf-8").splitlines()
        pending_comment: Optional[str] = None

        for lineno, raw in enumerate(lines, start=1):
            stripped = raw.strip()

            if stripped.startswith("#"):
                pending_comment = stripped.lstrip("# ").strip()
                continue

            if not stripped or "=" not in stripped:
                pending_comment = None
                continue

            key, _, rest = stripped.partition("=")
            key = key.strip()
            value = rest.strip().strip('"').strip("'")

            entry = AnnotatedKey(
                key=key,
                value=value,
                source=source,
                line_number=lineno,
                raw_line=raw,
                comment=pending_comment,
            )
            result.entries.append(entry)
            pending_comment = None

        return result
