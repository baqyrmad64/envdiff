"""Resolve .env file paths from environment name aliases or glob patterns."""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from typing import List, Optional


# Common naming conventions for env files
_PATTERNS = [
    ".env.{name}",
    ".env.{name}.local",
    "{name}.env",
    "envs/{name}.env",
    "config/{name}.env",
]


@dataclass
class ResolvedPath:
    alias: str
    path: str
    exists: bool

    def __str__(self) -> str:
        status = "ok" if self.exists else "missing"
        return f"{self.alias} -> {self.path} [{status}]"


@dataclass
class ResolverResult:
    resolved: List[ResolvedPath] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)

    @property
    def all_found(self) -> bool:
        return len(self.unresolved) == 0 and all(r.exists for r in self.resolved)


class EnvResolver:
    """Resolve environment name aliases to actual .env file paths."""

    def __init__(self, base_dir: str = ".") -> None:
        self.base_dir = base_dir

    def resolve(self, name: str) -> Optional[str]:
        """Try to find a matching .env file for the given alias."""
        # If it already looks like a file path, use it directly
        if name.endswith(".env") or os.sep in name or name.startswith("."):
            full = os.path.join(self.base_dir, name)
            return full if os.path.isfile(full) else None

        for pattern in _PATTERNS:
            candidate = os.path.join(self.base_dir, pattern.format(name=name))
            matches = glob.glob(candidate)
            if matches:
                return matches[0]

        return None

    def resolve_many(self, names: List[str]) -> ResolverResult:
        result = ResolverResult()
        for name in names:
            path = self.resolve(name)
            if path is None:
                result.unresolved.append(name)
            else:
                result.resolved.append(
                    ResolvedPath(alias=name, path=path, exists=os.path.isfile(path))
                )
        return result
