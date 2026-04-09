"""Tests for envdiff.snapshot module."""
import json
from pathlib import Path

import pytest

from envdiff.snapshot import EnvSnapshot, SnapshotManager


@pytest.fixture
def sample_data() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}


@pytest.fixture
def snapshot(sample_data) -> EnvSnapshot:
    return EnvSnapshot(source=".env.test", captured_at="2024-01-01T00:00:00+00:00", data=sample_data)


@pytest.fixture
def manager(tmp_path) -> SnapshotManager:
    return SnapshotManager(tmp_path / "snapshots")


def test_snapshot_checksum_is_deterministic(sample_data):
    s1 = EnvSnapshot(source="a", captured_at="t1", data=sample_data)
    s2 = EnvSnapshot(source="b", captured_at="t2", data=sample_data)
    assert s1.checksum == s2.checksum


def test_snapshot_checksum_changes_with_data():
    s1 = EnvSnapshot(source="a", captured_at="t", data={"KEY": "val1"})
    s2 = EnvSnapshot(source="a", captured_at="t", data={"KEY": "val2"})
    assert s1.checksum != s2.checksum


def test_is_identical_same_data(sample_data):
    s1 = EnvSnapshot(source="x", captured_at="t", data=sample_data)
    s2 = EnvSnapshot(source="y", captured_at="t2", data=dict(sample_data))
    assert s1.is_identical(s2)


def test_is_identical_different_data(sample_data):
    s1 = EnvSnapshot(source="x", captured_at="t", data=sample_data)
    s2 = EnvSnapshot(source="x", captured_at="t", data={**sample_data, "NEW_KEY": "val"})
    assert not s1.is_identical(s2)


def test_diff_keys_missing_in_other(snapshot):
    other = EnvSnapshot(source="b", captured_at="t", data={"DB_HOST": "localhost"})
    diff = snapshot.diff_keys(other)
    assert "DB_PORT" in diff
    assert diff["DB_PORT"] is None


def test_diff_keys_changed_value(snapshot):
    modified = dict(snapshot.data)
    modified["DB_HOST"] = "prod-db.example.com"
    other = EnvSnapshot(source="b", captured_at="t", data=modified)
    diff = snapshot.diff_keys(other)
    assert diff["DB_HOST"] == "prod-db.example.com"


def test_diff_keys_identical_returns_empty(snapshot):
    other = EnvSnapshot(source="b", captured_at="t", data=dict(snapshot.data))
    assert snapshot.diff_keys(other) == {}


def test_to_dict_contains_expected_keys(snapshot):
    d = snapshot.to_dict()
    assert set(d.keys()) == {"source", "captured_at", "checksum", "data"}


def test_manager_save_and_load(manager, sample_data):
    snap = manager.capture("env.test", sample_data)
    path = manager.save(snap)
    assert path.exists()
    loaded = manager.load(path)
    assert loaded.data == sample_data
    assert loaded.checksum == snap.checksum


def test_manager_list_snapshots(manager, sample_data):
    assert manager.list_snapshots() == []
    snap = manager.capture("env.test", sample_data)
    manager.save(snap)
    assert len(manager.list_snapshots()) == 1


def test_manager_creates_dir_if_missing(tmp_path):
    new_dir = tmp_path / "deep" / "nested" / "snaps"
    mgr = SnapshotManager(new_dir)
    assert new_dir.exists()
