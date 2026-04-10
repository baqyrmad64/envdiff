"""Tests for envdiff.scorer."""

import pytest
from unittest.mock import MagicMock

from envdiff.scorer import EnvScorer, EnvScore, ScoreBreakdown, _grade
from envdiff.comparator import ComparisonResult


@pytest.fixture
def scorer() -> EnvScorer:
    return EnvScorer()


@pytest.fixture
def clean_result() -> ComparisonResult:
    return ComparisonResult(missing_keys=[], extra_keys=[], mismatched_keys={})


@pytest.fixture
def dirty_result() -> ComparisonResult:
    return ComparisonResult(
        missing_keys=["DB_HOST", "SECRET_KEY"],
        extra_keys=["DEBUG"],
        mismatched_keys={"PORT": ("5432", "3306")},
    )


def test_score_clean_env_is_100(scorer, clean_result):
    result = scorer.score("production", clean_result)
    assert result.score == 100


def test_score_clean_env_grade_is_a(scorer, clean_result):
    result = scorer.score("production", clean_result)
    assert result.grade == "A"


def test_score_clean_env_is_healthy(scorer, clean_result):
    result = scorer.score("production", clean_result)
    assert result.is_healthy is True


def test_score_dirty_env_penalises_missing_keys(scorer, dirty_result):
    result = scorer.score("staging", dirty_result)
    # 2 missing * 10 + 1 extra * 3 + 1 mismatch * 7 = 30 penalty
    assert result.score == 70


def test_score_dirty_env_is_not_healthy(scorer, dirty_result):
    result = scorer.score("staging", dirty_result)
    assert result.is_healthy is False


def test_score_with_lint_report(scorer, clean_result):
    lint_report = MagicMock()
    lint_report.total_issues = 4
    result = scorer.score("dev", clean_result, lint_report=lint_report)
    assert result.score == 100 - (4 * 5)


def test_score_never_goes_below_zero(scorer):
    massive_result = ComparisonResult(
        missing_keys=[f"KEY_{i}" for i in range(20)],
        extra_keys=[],
        mismatched_keys={},
    )
    result = scorer.score("broken", massive_result)
    assert result.score == 0


def test_score_environment_name_stored(scorer, clean_result):
    result = scorer.score("production", clean_result)
    assert result.environment == "production"


def test_summary_contains_environment(scorer, dirty_result):
    result = scorer.score("staging", dirty_result)
    assert "staging" in result.summary()


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(85) == "B"
    assert _grade(70) == "C"
    assert _grade(55) == "D"
    assert _grade(30) == "F"
