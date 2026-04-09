"""Tests for the reporter module."""

import pytest
from envdiff.reporter import Report, ReportBuilder
from envdiff.comparator import ComparisonResult


@pytest.fixture
def clean_result():
    return ComparisonResult(
        missing_keys=[],
        extra_keys=[],
        mismatched_keys={},
    )


@pytest.fixture
def dirty_result():
    return ComparisonResult(
        missing_keys=["DB_HOST", "API_KEY"],
        extra_keys=["LEGACY_FLAG"],
        mismatched_keys={"PORT": ("8080", "9090")},
    )


def test_report_no_issues(clean_result):
    report = (
        ReportBuilder("base.env")
        .add_result("prod.env", clean_result)
        .build()
    )
    assert not report.has_issues
    assert report.summary["total_issues"] == 0


def test_report_with_issues(dirty_result):
    report = (
        ReportBuilder("base.env")
        .add_result("prod.env", dirty_result)
        .build()
    )
    assert report.has_issues
    assert report.summary["missing"] == 2
    assert report.summary["extra"] == 1
    assert report.summary["mismatched"] == 1
    assert report.summary["total_issues"] == 4


def test_report_multiple_targets(clean_result, dirty_result):
    report = (
        ReportBuilder("base.env")
        .add_result("staging.env", clean_result)
        .add_result("prod.env", dirty_result)
        .build()
    )
    assert report.has_issues
    assert len(report.target_files) == 2
    assert report.get_issues_for("staging.env") == clean_result
    assert report.get_issues_for("prod.env") == dirty_result


def test_get_issues_for_unknown_target(clean_result):
    report = ReportBuilder("base.env").add_result("dev.env", clean_result).build()
    assert report.get_issues_for("nonexistent.env") is None


def test_builder_chaining(clean_result, dirty_result):
    builder = ReportBuilder("base.env")
    result = builder.add_result("a.env", clean_result)
    assert result is builder  # ensure fluent interface returns self
