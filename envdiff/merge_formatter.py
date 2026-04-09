"""Format MergeResult for display in the CLI."""

from typing import Optional
from envdiff.merger import MergeResult

_MISSING = "<missing>"
_COL_WIDTH = 20


def _truncate(value: Optional[str], width: int = _COL_WIDTH) -> str:
    if value is None:
        return _MISSING.ljust(width)
    if len(value) > width:
        return (value[: width - 3] + "...").ljust(width)
    return value.ljust(width)


def format_merge_table(result: MergeResult, show_consistent: bool = False) -> str:
    """Render a table of merged keys across all environments."""
    lines = []
    env_names = result.env_names

    header = "KEY".ljust(30) + "  ".join(name.upper().ljust(_COL_WIDTH) for name in env_names)
    separator = "-" * len(header)
    lines.extend([header, separator])

    for key, merged_key in sorted(result.keys.items()):
        if not show_consistent and merged_key.is_consistent and not merged_key.missing_in:
            continue
        row = key.ljust(30)
        row += "  ".join(_truncate(merged_key.values.get(env)) for env in env_names)
        lines.append(row)

    if len(lines) == 2:
        lines.append("  (all keys consistent across environments)")

    return "\n".join(lines)


def format_merge_summary(result: MergeResult) -> str:
    """Return a short summary string for the merge result."""
    total = len(result.all_keys)
    inconsistent = len(result.inconsistent_keys)
    incomplete = len(result.incomplete_keys)
    return (
        f"Total keys: {total} | "
        f"Inconsistent values: {inconsistent} | "
        f"Missing in at least one env: {incomplete}"
    )
