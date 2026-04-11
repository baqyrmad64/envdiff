"""Format TemplateResult for display in the terminal."""
from envdiff.templater import TemplateResult


def _col(text: str, width: int) -> str:
    return text[:width].ljust(width)


def format_template_table(result: TemplateResult, show_optional: bool = True) -> str:
    keys = result.keys if show_optional else result.required_keys
    if not keys:
        return "No keys to display.\n"

    col_key = max(len(k.key) for k in keys)
    col_key = max(col_key, 10)
    col_ph = max(len(k.placeholder) for k in keys)
    col_ph = max(col_ph, 11)

    sep = f"+{'-' * (col_key + 2)}+{'-' * (col_ph + 2)}+{'-' * 10}+"
    header = (
        f"| {_col('KEY', col_key)} "
        f"| {_col('PLACEHOLDER', col_ph)} "
        f"| {'REQUIRED':<8} |"
    )

    lines = [sep, header, sep]
    for k in keys:
        req = "yes" if k.required else "no"
        row = (
            f"| {_col(k.key, col_key)} "
            f"| {_col(k.placeholder, col_ph)} "
            f"| {req:<8} |"
        )
        lines.append(row)
    lines.append(sep)
    return "\n".join(lines) + "\n"


def format_template_summary(result: TemplateResult) -> str:
    total = result.total_keys
    req = len(result.required_keys)
    opt = len(result.optional_keys)
    lines = [
        f"Template: {result.source_name}",
        f"  Total keys : {total}",
        f"  Required   : {req}",
        f"  Optional   : {opt}",
    ]
    return "\n".join(lines) + "\n"
