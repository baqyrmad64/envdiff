"""Tests for envdiff.baseline_formatter module."""
import pytest
from envdiff.baseline import BaselineDiff
from envdiff.baseline_formatter import format_baseline_diff, format_baseline_summary


@pytest.fixture
def clean_diff() -> BaselineDiff:
    return BaselineDiff()


@pytest.fixture
def dirty_diff() -> BaselineDiff:
    return BaselineDiff(
        added=["NEW_KEY"],
        removed=["OLD_KEY"],
        changed={"DB_HOST": ("localhost", "prod-db")},
    )


def test_clean_diff_shows_no_changes(clean_diff):
    out = format_baseline_diff(clean_diff)
    assert "No changes" in out


def test_clean_diff_with_source(clean_diff):
    out = format_baseline_diff(clean_diff, source="production")
    assert "production" in out


def test_dirty_diff_shows_added_key(dirty_diff):
    out = format_baseline_diff(dirty_diff)
    assert "NEW_KEY" in out


def test_dirty_diff_shows_removed_key(dirty_diff):
    out = format_baseline_diff(dirty_diff)
    assert "OLD_KEY" in out


def test_dirty_diff_shows_changed_key(dirty_diff):
    out = format_baseline_diff(dirty_diff)
    assert "DB_HOST" in out
    assert "localhost" in out
    assert "prod-db" in out


def test_dirty_diff_shows_summary(dirty_diff):
    out = format_baseline_diff(dirty_diff)
    assert "added" in out or "+1" in out
    assert "removed" in out or "-1" in out
    assert "changed" in out or "~1" in out


def test_format_baseline_summary_clean(clean_diff):
    out = format_baseline_summary({"prod": clean_diff})
    assert "prod" in out
    assert "no changes" in out


def test_format_baseline_summary_dirty(dirty_diff):
    out = format_baseline_summary({"staging": dirty_diff})
    assert "staging" in out
    assert "✘" in out


def test_format_baseline_summary_multiple(clean_diff, dirty_diff):
    out = format_baseline_summary({"prod": clean_diff, "staging": dirty_diff})
    assert "prod" in out
    assert "staging" in out
