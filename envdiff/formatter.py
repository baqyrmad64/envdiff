"""Output formatters for comparison results."""
import json
from typing import Dict, Any

from envdiff.comparator import ComparisonResult


class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def format_text(result: ComparisonResult, verbose: bool = False, use_color: bool = True) -> str:
    """Format comparison result as human-readable text."""
    lines = []
    c = Colors if use_color else type('NoColors', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()
    
    lines.append(f"{c.BOLD}Comparing: {result.target_name}{c.RESET}")
    lines.append("=" * 50)
    
    if not result.has_differences():
        lines.append(f"{c.GREEN}✓ No differences found{c.RESET}")
        return "\n".join(lines)
    
    summary = result.get_summary()
    
    if result.missing_keys:
        lines.append(f"\n{c.RED}Missing keys ({len(result.missing_keys)}):{c.RESET}")
        for key in sorted(result.missing_keys):
            lines.append(f"  - {key}")
    
    if result.extra_keys:
        lines.append(f"\n{c.YELLOW}Extra keys ({len(result.extra_keys)}):{c.RESET}")
        for key in sorted(result.extra_keys):
            lines.append(f"  + {key}")
    
    if result.mismatched_values and verbose:
        lines.append(f"\n{c.BLUE}Value mismatches ({len(result.mismatched_values)}):{c.RESET}")
        for key, values in sorted(result.mismatched_values.items()):
            lines.append(f"  ~ {key}")
            lines.append(f"    base:   {values['base']}")
            lines.append(f"    target: {values['target']}")
    elif result.mismatched_values:
        lines.append(f"\n{c.BLUE}Value mismatches: {len(result.mismatched_values)}{c.RESET}")
        lines.append("  (use --verbose to see details)")
    
    lines.append(f"\n{summary}")
    return "\n".join(lines)


def format_json(result: ComparisonResult, verbose: bool = False, **kwargs) -> str:
    """Format comparison result as JSON."""
    data: Dict[str, Any] = {
        "target": result.target_name,
        "has_differences": result.has_differences(),
        "missing_keys": sorted(result.missing_keys),
        "extra_keys": sorted(result.extra_keys),
    }
    
    if verbose:
        data["mismatched_values"] = result.mismatched_values
    else:
        data["mismatch_count"] = len(result.mismatched_values)
    
    return json.dumps(data, indent=2)


def format_table(result: ComparisonResult, verbose: bool = False, use_color: bool = True) -> str:
    """Format comparison result as a simple table."""
    lines = []
    c = Colors if use_color else type('NoColors', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()
    
    lines.append(f"Target: {result.target_name}")
    lines.append("-" * 50)
    lines.append(f"{'Status':<15} {'Count':<10} {'Type'}")
    lines.append("-" * 50)
    
    if result.missing_keys:
        lines.append(f"{c.RED}Missing{c.RESET:<24} {len(result.missing_keys):<10} Keys not in target")
    
    if result.extra_keys:
        lines.append(f"{c.YELLOW}Extra{c.RESET:<24} {len(result.extra_keys):<10} Keys only in target")
    
    if result.mismatched_values:
        lines.append(f"{c.BLUE}Mismatched{c.RESET:<24} {len(result.mismatched_values):<10} Different values")
    
    if not result.has_differences():
        lines.append(f"{c.GREEN}OK{c.RESET:<24} {'0':<10} No differences")
    
    return "\n".join(lines)


def format_output(result: ComparisonResult, format_type: str = "text", **kwargs) -> str:
    """Format comparison result based on specified format type."""
    formatters = {
        "text": format_text,
        "json": format_json,
        "table": format_table,
    }
    
    formatter = formatters.get(format_type, format_text)
    return formatter(result, **kwargs)
