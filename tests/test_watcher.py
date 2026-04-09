"""Tests for envdiff.watcher module."""

import os
import time
import pytest
from unittest.mock import MagicMock, patch
from envdiff.watcher import FileSnapshot, WatchEvent, EnvWatcher


@pytest.fixture
def tmp_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


def test_file_snapshot_from_path(tmp_env):
    snap = FileSnapshot.from_path(tmp_env)
    assert snap.path == tmp_env
    assert snap.mtime > 0
    assert snap.size > 0


def test_file_snapshot_no_change(tmp_env):
    snap = FileSnapshot.from_path(tmp_env)
    assert not snap.has_changed()


def test_file_snapshot_detects_change(tmp_env):
    snap = FileSnapshot.from_path(tmp_env)
    time.sleep(0.05)
    with open(tmp_env, "a") as f:
        f.write("NEW=1\n")
    assert snap.has_changed()


def test_file_snapshot_missing_file():
    snap = FileSnapshot(path="/nonexistent/.env", mtime=0.0, size=0)
    assert snap.has_changed()


def test_watch_event_has_timestamp():
    event = WatchEvent(changed_files=[".env"])
    assert event.timestamp > 0
    assert ".env" in event.changed_files


def test_watcher_calls_callback_on_change(tmp_env):
    watcher = EnvWatcher(paths=[tmp_env], interval=0.05)
    callback = MagicMock()
    watcher.on_change(callback)

    def modify_and_stop():
        time.sleep(0.08)
        with open(tmp_env, "a") as f:
            f.write("EXTRA=yes\n")

    import threading
    t = threading.Thread(target=modify_and_stop)
    t.start()
    watcher.start(max_iterations=4)
    t.join()

    assert callback.called
    event = callback.call_args[0][0]
    assert tmp_env in event.changed_files


def test_watcher_no_callback_on_no_change(tmp_env):
    watcher = EnvWatcher(paths=[tmp_env], interval=0.05)
    callback = MagicMock()
    watcher.on_change(callback)
    watcher.start(max_iterations=2)
    callback.assert_not_called()


def test_watcher_stop():
    watcher = EnvWatcher(paths=[], interval=0.05)
    watcher._running = True
    watcher.stop()
    assert not watcher._running
