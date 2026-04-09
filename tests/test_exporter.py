"""Tests for envdiff.exporter."""
import json
import csv
import io
from unittest.mock import MagicMock

import pytest

from envdiff.comparator import ComparisonResult
from envdiff.reporter import Report
from envdiff.exporter import export_json, export_csv, export_markdown, export_report


@pytest.fixture()
def clean_result() -> ComparisonResult:
    return ComparisonResult(missing_keys=set(), extra_keys=set(), mismatched_keys={})


@pytest.fixture()
def dirty_result() -> ComparisonResult:
    return ComparisonResult(
        missing_keys={"SECRET_KEY"},
        extra_keys={"DEBUG"},
        mismatched_keys={"DB_HOST": ("localhost", "db.prod.example.com")},
    )


@pytest.fixture()
def report(clean_result, dirty_result) -> Report:
    return Report(
        base_name=".env.base",
        target_names=["staging", "production"],
        results={"staging": clean_result, "production": dirty_result},
    )


class TestExportJson:
    def test_structure(self, report):
        data = json.loads(export_json(report))
        assert data["base"] == ".env.base"
        assert len(data["targets"]) == 2
        assert data["has_issues"] is True

    def test_clean_target(self, report):
        data = json.loads(export_json(report))
        staging = next(t for t in data["targets"] if t["name"] == "staging")
        assert staging["missing_keys"] == []
        assert staging["extra_keys"] == []
        assert staging["mismatched_keys"] == {}

    def test_dirty_target(self, report):
        data = json.loads(export_json(report))
        prod = next(t for t in data["targets"] if t["name"] == "production")
        assert "SECRET_KEY" in prod["missing_keys"]
        assert "DEBUG" in prod["extra_keys"]
        assert prod["mismatched_keys"]["DB_HOST"]["base"] == "localhost"


class TestExportCsv:
    def _rows(self, text):
        return list(csv.DictReader(io.StringIO(text)))

    def test_header_present(self, report):
        rows = self._rows(export_csv(report))
        assert set(rows[0].keys()) == {"target", "issue_type", "key", "base_value", "target_value"}

    def test_issues_recorded(self, report):
        rows = self._rows(export_csv(report))
        issue_types = {r["issue_type"] for r in rows}
        assert "missing" in issue_types
        assert "extra" in issue_types
        assert "mismatch" in issue_types

    def test_clean_target_no_rows(self, report):
        rows = self._rows(export_csv(report))
        staging_rows = [r for r in rows if r["target"] == "staging"]
        assert staging_rows == []


class TestExportMarkdown:
    def test_contains_base(self, report):
        md = export_markdown(report)
        assert ".env.base" in md

    def test_no_issues_message(self, report):
        md = export_markdown(report)
        assert "No issues found" in md

    def test_table_rendered(self, report):
        md = export_markdown(report)
        assert "DB_HOST" in md
        assert "db.prod.example.com" in md


def test_dispatch_invalid_format(report):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_report(report, "xml")  # type: ignore[arg-type]
