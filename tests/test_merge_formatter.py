"""Tests for envdiff.merge_formatter."""

import pytest
from envdiff.merger import EnvMerger
from envdiff.merge_formatter import format_merge_table, format_merge_summary


@pytest.fixture
def result():
    merger = EnvMerger()
    return merger.merge(
        {
            "dev": {"DB_HOST": "localhost", "PORT": "8080", "SECRET": "abc"},
            "prod": {"DB_HOST": "prod.db", "PORT": "8080"},
        }
    )


def test_table_has_header(result):
    table = format_merge_table(result)
    assert "DEV" in table
    assert "PROD" in table


def test_table_shows_inconsistent_key(result):
    table = format_merge_table(result)
    assert "DB_HOST" in table


def test_table_shows_missing_key(result):
    table = format_merge_table(result)
    assert "SECRET" in table
    assert "<missing>" in table


def test_table_hides_consistent_by_default(result):
    table = format_merge_table(result)
    # PORT is consistent and present in both — should be hidden
    assert "PORT" not in table


def test_table_shows_consistent_when_flag_set(result):
    table = format_merge_table(result, show_consistent=True)
    assert "PORT" in table


def test_table_all_consistent_message():
    merger = EnvMerger()
    r = merger.merge({"dev": {"X": "1"}, "prod": {"X": "1"}})
    table = format_merge_table(r)
    assert "all keys consistent" in table


def test_summary_contains_counts(result):
    summary = format_merge_summary(result)
    assert "Total keys:" in summary
    assert "Inconsistent values:" in summary
    assert "Missing in at least one env:" in summary


def test_summary_correct_total(result):
    summary = format_merge_summary(result)
    assert "Total keys: 3" in summary
