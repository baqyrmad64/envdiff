"""Format tag results for CLI output."""
from typing import Optional
from envdiff.tagger import TagResult

_COLORS = {
    "secret": "\033[91m",
    "database": "\033[94m",
    "url": "\033[96m",
    "aws": "\033[93m",
    "debug": "\033[90m",
    "feature_flag": "\033[95m",
    "email": "\033[36m",
    "port": "\033[33m",
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _color_tag(tag: str, use_color: bool) -> str:
    if not use_color:
        return f"[{tag}]" 
    color = _COLORS.get(tag, "\033[37m")
    return f"{color}[{tag}]{_RESET}"


def format_tag_table(result: TagResult, use_color: bool = True) -> str:
    lines = []
    header = f"{_BOLD}KEY{_RESET if use_color else ''}" if use_color else "KEY"
    lines.append(f"{header:<40}  TAGS")
    lines.append("-" * 60)
    for tagged in sorted(result.tagged, key=lambda t: t.key):
        tag_str = "  ".join(_color_tag(t, use_color) for t in tagged.tags)
        if not tag_str:
            tag_str = "(none)"
        lines.append(f"{tagged.key:<40}  {tag_str}")
    return "\n".join(lines)


def format_tag_summary(result: TagResult, use_color: bool = True) -> str:
    all_tags = result.all_tags()
    total = len(result.tagged)
    untagged = len(result.untagged_keys())
    lines = [
        f"Total keys : {total}",
        f"Untagged   : {untagged}",
        "",
        "Tag breakdown:",
    ]
    for tag in sorted(all_tags):
        count = len(result.keys_for_tag(tag))
        label = _color_tag(tag, use_color)
        lines.append(f"  {label:<30}  {count} key(s)")
    return "\n".join(lines)
