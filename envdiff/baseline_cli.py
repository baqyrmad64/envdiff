"""CLI helpers for baseline save/compare sub-commands."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

from envdiff.baseline import Baseline, BaselineManager
from envdiff.baseline_formatter import format_baseline_diff, format_baseline_summary
from envdiff.parser import parse_file

_DEFAULT_STORE = Path(".envdiff_baselines.json")


def _manager(store: Path | None = None) -> BaselineManager:
    return BaselineManager(store or _DEFAULT_STORE)


def cmd_baseline_save(source: str, env_path: str, store: Path | None = None) -> int:
    """Parse *env_path* and save it as the baseline for *source*. Returns exit code."""
    path = Path(env_path)
    if not path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 1
    entries: Dict[str, str] = parse_file(path)
    baseline = Baseline(source=source, entries=entries)
    _manager(store).save(baseline)
    print(f"Baseline saved for '{source}' ({len(entries)} keys).")
    return 0


def cmd_baseline_compare(
    source: str,
    env_path: str,
    store: Path | None = None,
    quiet: bool = False,
) -> int:
    """Compare *env_path* against the stored baseline for *source*. Returns exit code."""
    path = Path(env_path)
    if not path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 1

    mgr = _manager(store)
    current: Dict[str, str] = parse_file(path)
    diff = mgr.compare(source, current)

    if diff is None:
        print(f"No baseline found for '{source}'. Run 'baseline save' first.", file=sys.stderr)
        return 2

    if not quiet:
        print(format_baseline_diff(diff, source=source))

    return 0 if diff.is_clean else 1


def cmd_baseline_status(store: Path | None = None) -> int:
    """Print a summary of all stored baselines."""
    store_path = store or _DEFAULT_STORE
    if not store_path.exists():
        print("No baselines stored yet.")
        return 0

    import json
    from envdiff.baseline import Baseline, BaselineDiff

    data = json.loads(store_path.read_text())
    if not data:
        print("No baselines stored yet.")
        return 0

    diffs: dict[str, BaselineDiff] = {}
    for source, raw in data.items():
        b = Baseline.from_dict(raw)
        diffs[source] = BaselineDiff()  # stored baselines are always "clean" by definition
        _ = b  # just listing them

    print(f"Stored baselines ({len(data)}):")
    for source in data:
        print(f"  • {source}")
    return 0
