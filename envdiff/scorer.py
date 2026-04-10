"""Scores an environment's overall health based on lint, validation, and diff results."""

from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import ComparisonResult
from envdiff.linter import LintReport


PENALTY_MISSING_KEY = 10
PENALTY_EXTRA_KEY = 3
PENALTY_LINT_ISSUE = 5
PENALTY_MISMATCH = 7
MAX_SCORE = 100


@dataclass
class ScoreBreakdown:
    missing_keys: int = 0
    extra_keys: int = 0
    lint_issues: int = 0
    mismatched_keys: int = 0

    @property
    def total_penalty(self) -> int:
        return (
            self.missing_keys * PENALTY_MISSING_KEY
            + self.extra_keys * PENALTY_EXTRA_KEY
            + self.lint_issues * PENALTY_LINT_ISSUE
            + self.mismatched_keys * PENALTY_MISMATCH
        )


@dataclass
class EnvScore:
    environment: str
    score: int
    breakdown: ScoreBreakdown
    grade: str = field(init=False)

    def __post_init__(self) -> None:
        self.grade = _grade(self.score)

    @property
    def is_healthy(self) -> bool:
        return self.score >= 80

    def summary(self) -> str:
        return (
            f"{self.environment}: {self.score}/100 ({self.grade}) — "
            f"missing={self.breakdown.missing_keys}, "
            f"extra={self.breakdown.extra_keys}, "
            f"lint={self.breakdown.lint_issues}, "
            f"mismatch={self.breakdown.mismatched_keys}"
        )


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


class EnvScorer:
    """Produces an EnvScore for a given environment using comparison and lint data."""

    def score(
        self,
        environment: str,
        result: ComparisonResult,
        lint_report: LintReport | None = None,
    ) -> EnvScore:
        breakdown = ScoreBreakdown(
            missing_keys=len(result.missing_keys),
            extra_keys=len(result.extra_keys),
            mismatched_keys=len(result.mismatched_keys),
            lint_issues=lint_report.total_issues if lint_report else 0,
        )
        raw = MAX_SCORE - breakdown.total_penalty
        final_score = max(0, min(MAX_SCORE, raw))
        return EnvScore(environment=environment, score=final_score, breakdown=breakdown)
