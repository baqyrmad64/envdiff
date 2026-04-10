"""Formats grouped env key output for display."""
from envdiff.grouper import GroupResult
from envdiff.formatter import Colors, format_text

_COL_WIDTH = 30


def _header(text: str) -> str:
    return format_text(f"  [{text}]", Colors.CYAN, bold=True)


def format_group_table(result: GroupResult, show_ungrouped: bool = True) -> str:
    lines = []
    lines.append(format_text("Key Groups", Colors.BOLD))
    lines.append("-" * 40)

    for prefix in result.all_prefixes():
        group = result.groups[prefix]
        lines.append(_header(f"{prefix}_* ({group.size()} keys)"))
        for key in group.keys:
            lines.append(f"    {key}")

    if show_ungrouped and result.ungrouped:
        lines.append(_header(f"ungrouped ({len(result.ungrouped)} keys)"))
        for key in result.ungrouped:
            lines.append(f"    {key}")

    return "\n".join(lines)


def format_group_summary(result: GroupResult) -> str:
    total_groups = len(result.groups)
    total_grouped = result.total_grouped()
    total_ungrouped = len(result.ungrouped)
    total_keys = total_grouped + total_ungrouped

    lines = [
        format_text("Group Summary", Colors.BOLD),
        f"  Total keys    : {total_keys}",
        f"  Groups found  : {total_groups}",
        f"  Grouped keys  : {total_grouped}",
        f"  Ungrouped keys: {total_ungrouped}",
    ]
    return "\n".join(lines)
