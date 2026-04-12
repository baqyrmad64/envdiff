"""Format annotation results for terminal output."""
from __future__ import annotations

from envdiff.annotator import AnnotationResult
from envdiff.formatter import Colors, format_text


def _col(text: str, width: int) -> str:
    return text[:width].ljust(width)


def format_annotation_table(result: AnnotationResult, show_all: bool = False) -> str:
    if not result.entries:
        return format_text(f"No entries found in {result.source}", Colors.YELLOW)

    entries = result.entries if show_all else result.with_comments()
    if not entries:
        return format_text("No annotated keys found.", Colors.YELLOW)

    header = (
        format_text(_col("LINE", 6), Colors.BOLD)
        + format_text(_col("KEY", 28), Colors.BOLD)
        + format_text(_col("COMMENT", 44), Colors.BOLD)
    )
    divider = "-" * 78
    rows = [header, divider]

    for entry in entries:
        line_col = _col(str(entry.line_number), 6)
        key_col = _col(entry.key, 28)
        comment_col = _col(entry.comment or "", 44)
        rows.append(
            format_text(line_col, Colors.CYAN)
            + format_text(key_col, Colors.WHITE)
            + format_text(comment_col, Colors.GREEN)
        )

    return "\n".join(rows)


def format_annotation_summary(result: AnnotationResult) -> str:
    total = len(result.entries)
    annotated = len(result.with_comments())
    ratio = (annotated / total * 100) if total else 0
    color = Colors.GREEN if ratio >= 50 else Colors.YELLOW
    return (
        format_text(f"Source : {result.source}", Colors.BOLD) + "\n"
        + f"Total keys : {total}\n"
        + format_text(f"Annotated  : {annotated} ({ratio:.0f}%)", color)
    )
