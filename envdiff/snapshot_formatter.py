"""Format snapshot comparison results for display."""
from __future__ import annotations

from typing import Optional

from envdiff.snapshot import EnvSnapshot

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _col(text: str, color: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_snapshot_diff(
    base: EnvSnapshot,
    target: EnvSnapshot,
    use_color: bool = True,
    show_identical: bool = False,
) -> str:
    """Render a human-readable diff between two snapshots."""
    lines: list[str] = []
    header = f"Snapshot diff: {base.source!r} → {target.source!r}"
    lines.append(_col(header, _BOLD, use_color))
    lines.append(f"Base checksum   : {base.checksum}")
    lines.append(f"Target checksum : {target.checksum}")
    lines.append("")

    if base.is_identical(target):
        lines.append(_col("✓ Snapshots are identical.", _GREEN, use_color))
        return "\n".join(lines)

    all_keys = sorted(set(base.data) | set(target.data))

    for key in all_keys:
        in_base = key in base.data
        in_target = key in target.data

        if in_base and in_target:
            if base.data[key] == target.data[key]:
                if show_identical:
                    lines.append(f"  {key} = {base.data[key]}")
            else:
                b_val = _col(base.data[key], _YELLOW, use_color)
                t_val = _col(target.data[key], _YELLOW, use_color)
                lines.append(f"~ {key}: {b_val} → {t_val}")
        elif in_base:
            label = _col(f"- {key} = {base.data[key]}", _RED, use_color)
            lines.append(label)
        else:
            label = _col(f"+ {key} = {target.data[key]}", _GREEN, use_color)
            lines.append(label)

    return "\n".join(lines)


def format_snapshot_summary(base: EnvSnapshot, target: EnvSnapshot) -> str:
    """One-line summary of differences between two snapshots."""
    diff = base.diff_keys(target)
    missing = sum(1 for v in diff.values() if v is None)
    changed = sum(1 for v in diff.values() if v is not None)
    added = len(set(target.data) - set(base.data))
    return (
        f"{base.source!r} vs {target.source!r}: "
        f"{changed} changed, {missing} removed, {added} added"
    )
