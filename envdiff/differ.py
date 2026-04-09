"""Value-level diff utilities for comparing individual env variable values."""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class ValueDiff:
    key: str
    base_value: str
    target_value: str
    environment: str

    @property
    def is_empty_vs_set(self) -> bool:
        """One side is empty/missing value while the other has content."""
        return bool(self.base_value) != bool(self.target_value)

    @property
    def is_type_mismatch(self) -> bool:
        """Values look like different types (e.g. number vs string)."""
        return _looks_numeric(self.base_value) != _looks_numeric(self.target_value)

    @property
    def is_url_vs_localhost(self) -> bool:
        """One value is a real URL, the other is localhost."""
        return _is_localhost(self.base_value) != _is_localhost(self.target_value)

    def describe(self) -> str:
        hints = []
        if self.is_empty_vs_set:
            hints.append("one side is empty")
        if self.is_type_mismatch:
            hints.append("possible type mismatch")
        if self.is_url_vs_localhost:
            hints.append("localhost vs real URL")
        hint_str = f" ({', '.join(hints)})" if hints else ""
        return (
            f"[{self.environment}] {self.key}: "
            f"{self.base_value!r} -> {self.target_value!r}{hint_str}"
        )


def _looks_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _is_localhost(value: str) -> bool:
    return bool(re.search(r'localhost|127\.0\.0\.1', value or "", re.IGNORECASE))


def diff_values(
    base: dict[str, str],
    target: dict[str, str],
    environment: str,
) -> list[ValueDiff]:
    """Return ValueDiff entries for keys present in both but with different values."""
    diffs = []
    common_keys = set(base.keys()) & set(target.keys())
    for key in sorted(common_keys):
        if base[key] != target[key]:
            diffs.append(ValueDiff(
                key=key,
                base_value=base[key],
                target_value=target[key],
                environment=environment,
            ))
    return diffs
