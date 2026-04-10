"""Tests for envdiff.auditor"""

import pytest
from envdiff.auditor import AuditEntry, AuditLog
from envdiff.comparator import ComparisonResult


@pytest.fixture
def clean_result():
    return ComparisonResult(
        missing_keys=set(),
        extra_keys=set(),
        mismatched_keys=set(),
    )


@pytest.fixture
def dirty_result():
    return ComparisonResult(
        missing_keys={"DB_HOST"},
        extra_keys={"DEBUG"},
        mismatched_keys={"API_URL"},
    )


@pytest.fixture
def log():
    return AuditLog()


def test_entry_from_clean_result(clean_result):
    entry = AuditEntry.from_result(clean_result, "base", "prod")
    assert entry.is_clean()
    assert entry.total_issues == 0
    assert entry.base_env == "base"
    assert entry.target_env == "prod"


def test_entry_from_dirty_result(dirty_result):
    entry = AuditEntry.from_result(dirty_result, "base", "staging")
    assert not entry.is_clean()
    assert entry.total_issues == 3
    assert "DB_HOST" in entry.missing_keys
    assert "DEBUG" in entry.extra_keys
    assert "API_URL" in entry.mismatched_keys


def test_entry_has_timestamp(clean_result):
    entry = AuditEntry.from_result(clean_result, "base", "prod")
    assert entry.timestamp is not None
    assert "T" in entry.timestamp  # ISO format


def test_entry_note_is_optional(clean_result):
    entry = AuditEntry.from_result(clean_result, "base", "prod", note="nightly check")
    assert entry.note == "nightly check"


def test_entry_to_dict(dirty_result):
    entry = AuditEntry.from_result(dirty_result, "base", "prod")
    d = entry.to_dict()
    assert d["base_env"] == "base"
    assert d["total_issues"] == 3
    assert isinstance(d["missing_keys"], list)


def test_log_record_and_summary(log, clean_result, dirty_result):
    log.record(AuditEntry.from_result(clean_result, "base", "prod"))
    log.record(AuditEntry.from_result(dirty_result, "base", "staging"))
    summary = log.summary()
    assert summary["total_runs"] == 2
    assert summary["clean_runs"] == 1
    assert summary["dirty_runs"] == 1


def test_log_to_dict_structure(log, clean_result):
    log.record(AuditEntry.from_result(clean_result, "base", "prod"))
    d = log.to_dict()
    assert "summary" in d
    assert "entries" in d
    assert len(d["entries"]) == 1


def test_empty_log_summary(log):
    summary = log.summary()
    assert summary["total_runs"] == 0
    assert summary["clean_runs"] == 0
    assert summary["dirty_runs"] == 0
