"""Tests for envdiff.baseline module."""
import json
import pytest
from pathlib import Path

from envdiff.baseline import Baseline, BaselineDiff, BaselineManager


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / ".envdiff_baselines.json"


@pytest.fixture
def manager(store: Path) -> BaselineManager:
    return BaselineManager(store)


@pytest.fixture
def sample_baseline() -> Baseline:
    return Baseline(source="production", entries={"DB_HOST": "prod-db", "PORT": "5432"})


def test_baseline_to_dict(sample_baseline):
    d = sample_baseline.to_dict()
    assert d["source"] == "production"
    assert d["entries"]["PORT"] == "5432"


def test_baseline_from_dict(sample_baseline):
    restored = Baseline.from_dict(sample_baseline.to_dict())
    assert restored.source == sample_baseline.source
    assert restored.entries == sample_baseline.entries


def test_manager_save_and_load(manager, sample_baseline, store):
    manager.save(sample_baseline)
    assert store.exists()
    loaded = manager.load("production")
    assert loaded is not None
    assert loaded.entries["DB_HOST"] == "prod-db"


def test_manager_load_missing_source(manager):
    assert manager.load("nonexistent") is None


def test_manager_load_no_file(manager):
    assert manager.load("anything") is None


def test_manager_save_multiple_sources(manager):
    manager.save(Baseline(source="prod", entries={"A": "1"}))
    manager.save(Baseline(source="staging", entries={"A": "2"}))
    assert manager.load("prod").entries["A"] == "1"
    assert manager.load("staging").entries["A"] == "2"


def test_compare_no_changes(manager, sample_baseline):
    manager.save(sample_baseline)
    diff = manager.compare("production", {"DB_HOST": "prod-db", "PORT": "5432"})
    assert diff is not None
    assert diff.is_clean


def test_compare_added_key(manager, sample_baseline):
    manager.save(sample_baseline)
    diff = manager.compare("production", {"DB_HOST": "prod-db", "PORT": "5432", "NEW": "val"})
    assert "NEW" in diff.added


def test_compare_removed_key(manager, sample_baseline):
    manager.save(sample_baseline)
    diff = manager.compare("production", {"DB_HOST": "prod-db"})
    assert "PORT" in diff.removed


def test_compare_changed_key(manager, sample_baseline):
    manager.save(sample_baseline)
    diff = manager.compare("production", {"DB_HOST": "new-db", "PORT": "5432"})
    assert "DB_HOST" in diff.changed
    assert diff.changed["DB_HOST"] == ("prod-db", "new-db")


def test_compare_missing_baseline(manager):
    diff = manager.compare("ghost", {"A": "1"})
    assert diff is None


def test_baseline_diff_summary_clean():
    d = BaselineDiff()
    assert d.summary() == "no changes"


def test_baseline_diff_summary_mixed():
    d = BaselineDiff(added=["X"], removed=["Y", "Z"], changed={"A": ("old", "new")})
    s = d.summary()
    assert "+1" in s
    assert "-2" in s
    assert "~1" in s
