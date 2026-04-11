from envdiff.differ import ValueDiff
from envdiff.formatter import Colors, format_text
from typing import List


def _col(text: str, width: int) -> str:
    return text[:width].ljust(width)


def _diff_color(diff: ValueDiff) -> str:
    if diff.is_empty_vs_set():
        return Colors.YELLOW
    if diff.is_type_mismatch():
        return Colors.CYAN
    if diff.is_url_vs_localhost():
        return Colors.RED
    return Colors.RESET


def format_diff_table(diffs: List[ValueDiff], use_color: bool = True) -> str:
    if not diffs:
        return "No value differences found."

    header = f"{'KEY':<30} {'BASE':<25} {'TARGET':<25} {'NOTE':<30}"
    separator = "-" * len(header)
    lines = [header, separator]

    for diff in diffs:
        color = _diff_color(diff) if use_color else ""
        reset = Colors.RESET if use_color else ""
        note = diff.describe()
        row = f"{_col(diff.key, 30)} {_col(diff.base_value or '', 25)} {_col(diff.target_value or '', 25)} {_col(note, 30)}"
        lines.append(f"{color}{row}{reset}")

    return "\n".join(lines)


def format_diff_summary(diffs: List[ValueDiff]) -> str:
    if not diffs:
        return "All compared values are identical."

    total = len(diffs)
    empty_vs_set = sum(1 for d in diffs if d.is_empty_vs_set())
    type_mismatch = sum(1 for d in diffs if d.is_type_mismatch())
    localhost = sum(1 for d in diffs if d.is_url_vs_localhost())
    other = total - empty_vs_set - type_mismatch - localhost

    parts = [f"Total diffs: {total}"]
    if empty_vs_set:
        parts.append(f"  empty vs set: {empty_vs_set}")
    if type_mismatch:
        parts.append(f"  type mismatch: {type_mismatch}")
    if localhost:
        parts.append(f"  localhost issue: {localhost}")
    if other:
        parts.append(f"  other: {other}")

    return "\n".join(parts)
