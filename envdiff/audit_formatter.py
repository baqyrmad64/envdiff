"""Formatting helpers for AuditLog output."""

from typing import List
from envdiff.auditor import AuditEntry, AuditLog

_PASS = "\033[32m✔\033[0m"
_FAIL = "\033[31m✘\033[0m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _status_icon(entry: AuditEntry) -> str:
    return _PASS if entry.is_clean() else _FAIL


def format_entry_line(entry: AuditEntry) -> str:
    icon = _status_icon(entry)
    ts = entry.timestamp[:19].replace("T", " ")
    note = f" [{entry.note}]" if entry.note else ""
    issues = f"{entry.total_issues} issue(s)" if not entry.is_clean() else "clean"
    return f"{icon} {ts}  {entry.base_env} → {entry.target_env}  {issues}{note}"


def format_audit_table(log: AuditLog, show_clean: bool = True) -> str:
    lines: List[str] = []
    header = f"{_BOLD}Audit Log{_RESET}"
    lines.append(header)
    lines.append("-" * 60)

    entries = log.entries if show_clean else log.dirty_runs()
    if not entries:
        lines.append("  (no entries)")
    else:
        for entry in entries:
            lines.append("  " + format_entry_line(entry))

    lines.append("-" * 60)
    s = log.summary()
    lines.append(f"Total: {s['total_runs']}  Clean: {s['clean_runs']}  Dirty: {s['dirty_runs']}")
    return "\n".join(lines)


def format_audit_summary(log: AuditLog) -> str:
    s = log.summary()
    if s["total_runs"] == 0:
        return "No audit entries recorded."
    pct = round(100 * s["clean_runs"] / s["total_runs"])
    return (
        f"{s['total_runs']} run(s) audited — "
        f"{s['clean_runs']} clean ({pct}%), "
        f"{s['dirty_runs']} with issues."
    )
