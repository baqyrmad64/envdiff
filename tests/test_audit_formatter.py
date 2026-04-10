"""Tests for envdiff.audit_formatter"""

import pytest
from envdiff.auditor import AuditEntry, AuditLog
from envdiff.comparator import ComparisonResult
from envdiff.audit_formatter import format_entry_line, format_audit_table, format_audit_summary


@pytest.fixture
def clean_entry():
    result = ComparisonResult(missing_keys=set(), extra_keys=set(), mismatched_keys=set())
    return AuditEntry.from_result(result, "base", "prod")


@pytest.fixture
def dirty_entry():
    result = ComparisonResult(
        missing_keys={"DB_HOST", "SECRET_KEY"},
        extra_keys=set(),
        mismatched_keys=set(),
    )
    return AuditEntry.from_result(result, "base", "staging", note="manual run")


@pytest.fixture
def populated_log(clean_entry, dirty_entry):
    log = AuditLog()
    log.record(clean_entry)
    log.record(dirty_entry)
    return log


def test_format_entry_line_clean(clean_entry):
    line = format_entry_line(clean_entry)
    assert "clean" in line
    assert "base" in line
    assert "prod" in line


def test_format_entry_line_dirty(dirty_entry):
    line = format_entry_line(dirty_entry)
    assert "issue" in line
    assert "staging" in line


def test_format_entry_line_shows_note(dirty_entry):
    line = format_entry_line(dirty_entry)
    assert "manual run" in line


def test_format_entry_line_no_note(clean_entry):
    line = format_entry_line(clean_entry)
    assert "[" not in line


def test_format_audit_table_contains_header(populated_log):
    table = format_audit_table(populated_log)
    assert "Audit Log" in table


def test_format_audit_table_shows_both_entries(populated_log):
    table = format_audit_table(populated_log)
    assert "prod" in table
    assert "staging" in table


def test_format_audit_table_hide_clean(populated_log):
    table = format_audit_table(populated_log, show_clean=False)
    assert "staging" in table
    assert "prod" not in table


def test_format_audit_summary_empty():
    log = AuditLog()
    result = format_audit_summary(log)
    assert "No audit" in result


def test_format_audit_summary_percentage(populated_log):
    result = format_audit_summary(populated_log)
    assert "50%" in result
    assert "2 run" in result
