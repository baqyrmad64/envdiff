"""Key ignore list support — filter keys from comparison based on patterns."""

from __future__ import annotations

import fnmatch
from typing import Dict, Iterable, List, Set


class IgnoreList:
    """Holds a set of key patterns to exclude from comparison."""

    def __init__(self, patterns: Iterable[str] = ()) -> None:
        self._patterns: List[str] = list(patterns)

    def add(self, pattern: str) -> None:
        if pattern not in self._patterns:
            self._patterns.append(pattern)

    def remove(self, pattern: str) -> None:
        """Remove a pattern from the ignore list. Raises ValueError if not present."""
        try:
            self._patterns.remove(pattern)
        except ValueError:
            raise ValueError(f"Pattern {pattern!r} not found in ignore list")

    def should_ignore(self, key: str) -> bool:
        """Return True if the key matches any ignore pattern."""
        for pattern in self._patterns:
            if fnmatch.fnmatch(key, pattern):
                return True
        return False

    def filter_dict(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of env with ignored keys removed."""
        return {k: v for k, v in env.items() if not self.should_ignore(k)}

    def filter_keys(self, keys: Iterable[str]) -> Set[str]:
        """Return the set of keys that are NOT ignored."""
        return {k for k in keys if not self.should_ignore(k)}

    @property
    def patterns(self) -> List[str]:
        return list(self._patterns)

    def __len__(self) -> int:
        return len(self._patterns)

    def __repr__(self) -> str:
        return f"IgnoreList(patterns={self._patterns!r})"


def build_ignore_list(patterns: Iterable[str]) -> IgnoreList:
    return IgnoreList(patterns)
