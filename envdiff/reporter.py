"""Report generation for env diff results."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdiff.comparator import ComparisonResult


@dataclass
class Report:
    """Structured report of comparison results across environments."""

    base_file: str
    target_files: List[str]
    results: Dict[str, ComparisonResult]
    summary: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.summary = self._build_summary()

    def _build_summary(self) -> Dict[str, int]:
        total_missing = sum(len(r.missing_keys) for r in self.results.values())
        total_extra = sum(len(r.extra_keys) for r in self.results.values())
        total_mismatched = sum(len(r.mismatched_keys) for r in self.results.values())
        return {
            "missing": total_missing,
            "extra": total_extra,
            "mismatched": total_mismatched,
            "total_issues": total_missing + total_extra + total_mismatched,
        }

    @property
    def has_issues(self) -> bool:
        return self.summary["total_issues"] > 0

    def get_issues_for(self, target: str) -> Optional[ComparisonResult]:
        return self.results.get(target)


class ReportBuilder:
    """Builds a Report from comparison results."""

    def __init__(self, base_file: str):
        self.base_file = base_file
        self._results: Dict[str, ComparisonResult] = {}

    def add_result(self, target_file: str, result: ComparisonResult) -> "ReportBuilder":
        self._results[target_file] = result
        return self

    def build(self) -> Report:
        return Report(
            base_file=self.base_file,
            target_files=list(self._results.keys()),
            results=self._results,
        )
