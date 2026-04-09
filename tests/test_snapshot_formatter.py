"""Tests for envdiff.snapshot_formatter module."""
import pytest

from envdiff.snapshot import EnvSnapshot
from envdiff.snapshot_formatter import format_snapshot_diff, format_snapshot_summary


@pytest.fixture
def base() -> EnvSnapshot:
    return EnvSnapshot(
        source=".env.base",
        captured_at="2024-01-01T00:00:00+00:00",
        data={"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"},
    )


@pytest.fixture
def target() -> EnvSnapshot:
    return EnvSnapshot(
        source=".env.prod",
        captured_at="2024-01-02T00:00:00+00:00",
        data={"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "xyz"},
    )


def test_diff_header_contains_sources(base, target):
    out = format_snapshot_diff(base, target, use_color=False)
    assert ".env.base" in out
    assert ".env.prod" in out


def test_diff_shows_changed_key(base, target):
    out = format_snapshot_diff(base, target, use_color=False)
    assert "DB_HOST" in out
    assert "localhost" in out
    assert "prod.db" in out


def test_diff_shows_removed_key(base, target):
    out = format_snapshot_diff(base, target, use_color=False)
    assert "SECRET" in out
    assert "- SECRET" in out


def test_diff_shows_added_key(base, target):
    out = format_snapshot_diff(base, target, use_color=False)
    assert "+ API_KEY" in out


def test_diff_identical_snapshots():
    data = {"KEY": "val"}
    s1 = EnvSnapshot(source="a", captured_at="t", data=data)
    s2 = EnvSnapshot(source="b", captured_at="t", data=dict(data))
    out = format_snapshot_diff(s1, s2, use_color=False)
    assert "identical" in out.lower()


def test_diff_show_identical_flag(base):
    same = EnvSnapshot(source="b", captured_at="t", data=dict(base.data))
    # With show_identical=True on non-identical snapshots, unchanged keys appear
    modified = dict(base.data)
    modified["DB_HOST"] = "other"
    target2 = EnvSnapshot(source="c", captured_at="t", data=modified)
    out = format_snapshot_diff(base, target2, use_color=False, show_identical=True)
    assert "DB_PORT" in out


def test_summary_format(base, target):
    summary = format_snapshot_summary(base, target)
    assert ".env.base" in summary
    assert ".env.prod" in summary
    assert "changed" in summary
    assert "removed" in summary
    assert "added" in summary


def test_summary_counts_correctly(base, target):
    summary = format_snapshot_summary(base, target)
    # DB_HOST changed=1, SECRET removed=1, API_KEY added=1
    assert "1 changed" in summary
    assert "1 removed" in summary
    assert "1 added" in summary
