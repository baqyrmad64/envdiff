"""Format BaselineDiff results for terminal output."""
from __future__ import annotations

from envdiff.baseline import BaselineDiff
from envdiff.formatter import Colors, format_text


def _col(text: str, width: int) -> str:
    return text[:width].ljust(width)


def format_baseline_diff(diff: BaselineDiff, source: str = "") -> str:
    if diff.is_clean:
        return format_text(f"  ✔  No changes from baseline{' for ' + source if source else ''}.", Colors.GREEN)

    lines = []
    header = f"  Baseline diff{' — ' + source if source else ''}"
    lines.append(format_text(header, Colors.BOLD))
    lines.append("  " + "-" * 56)

    col_w = [20, 16, 16]
    header_row = (
        _col("KEY", col_w[0])
        + _col("BASELINE", col_w[1])
        + _col("CURRENT", col_w[2])
    )
    lines.append("  " + format_text(header_row, Colors.BOLD))

    for key in sorted(diff.added):
        row = _col(key, col_w[0]) + _col("(missing)", col_w[1]) + _col("<set>", col_w[2])
        lines.append("  " + format_text(row, Colors.GREEN))

    for key in sorted(diff.removed):
        row = _col(key, col_w[0]) + _col("<set>", col_w[1]) + _col("(missing)", col_w[2])
        lines.append("  " + format_text(row, Colors.RED))

    for key in sorted(diff.changed):
        old_val, new_val = diff.changed[key]
        row = (
            _col(key, col_w[0])
            + _col(old_val[:14], col_w[1])
            + _col(new_val[:14], col_w[2])
        )
        lines.append("  " + format_text(row, Colors.YELLOW))

    lines.append("")
    lines.append("  " + format_text(diff.summary(), Colors.BOLD))
    return "\n".join(lines)


def format_baseline_summary(diffs: dict[str, BaselineDiff]) -> str:
    lines = [format_text("  Baseline Summary", Colors.BOLD)]
    for source, diff in diffs.items():
        icon = "✔" if diff.is_clean else "✘"
        color = Colors.GREEN if diff.is_clean else Colors.RED
        lines.append("  " + format_text(f"{icon}  {source}: {diff.summary()}", color))
    return "\n".join(lines)
