"""Export diff results to various file formats."""
from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from envdiff.reporter import Report

ExportFormat = Literal["json", "csv", "markdown"]


def export_json(report: Report) -> str:
    """Serialize a Report to a JSON string."""
    payload = {
        "base": report.base_name,
        "targets": [
            {
                "name": target,
                "missing_keys": list(report.get_issues_for(target).missing_keys),
                "extra_keys": list(report.get_issues_for(target).extra_keys),
                "mismatched_keys": {
                    k: {"base": v[0], "target": v[1]}
                    for k, v in report.get_issues_for(target).mismatched_keys.items()
                },
            }
            for target in report.target_names
        ],
        "has_issues": report.has_issues,
    }
    return json.dumps(payload, indent=2)


def export_csv(report: Report) -> str:
    """Serialize a Report to a CSV string (one row per issue)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["target", "issue_type", "key", "base_value", "target_value"])
    for target in report.target_names:
        result = report.get_issues_for(target)
        for key in result.missing_keys:
            writer.writerow([target, "missing", key, "", ""])
        for key in result.extra_keys:
            writer.writerow([target, "extra", key, "", ""])
        for key, (base_val, tgt_val) in result.mismatched_keys.items():
            writer.writerow([target, "mismatch", key, base_val, tgt_val])
    return buf.getvalue()


def export_markdown(report: Report) -> str:
    """Serialize a Report to a Markdown string."""
    lines = [f"# envdiff report\n", f"**Base:** `{report.base_name}`\n"]
    for target in report.target_names:
        result = report.get_issues_for(target)
        lines.append(f"## {target}\n")
        if not result.missing_keys and not result.extra_keys and not result.mismatched_keys:
            lines.append("_No issues found._\n")
            continue
        if result.missing_keys:
            lines.append("**Missing keys:** " + ", ".join(f"`{k}`" for k in sorted(result.missing_keys)) + "\n")
        if result.extra_keys:
            lines.append("**Extra keys:** " + ", ".join(f"`{k}`" for k in sorted(result.extra_keys)) + "\n")
        if result.mismatched_keys:
            lines.append("**Mismatched keys:**\n")
            lines.append("| Key | Base | Target |")
            lines.append("|-----|------|--------|")
            for key, (base_val, tgt_val) in sorted(result.mismatched_keys.items()):
                lines.append(f"| `{key}` | `{base_val}` | `{tgt_val}` |")
            lines.append("")
    return "\n".join(lines)


def export_report(report: Report, fmt: ExportFormat) -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(report)
    if fmt == "csv":
        return export_csv(report)
    if fmt == "markdown":
        return export_markdown(report)
    raise ValueError(f"Unsupported export format: {fmt!r}")


def write_export(report: Report, fmt: ExportFormat, dest: Path) -> None:
    """Export *report* and write it to *dest*."""
    dest.write_text(export_report(report, fmt), encoding="utf-8")
