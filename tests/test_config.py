"""Tests for envdiff.config."""

import json
import os
import pytest

from envdiff.config import EnvDiffConfig, find_config_file, load_config


@pytest.fixture
def config_dir(tmp_path):
    return tmp_path


def write_config(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def test_default_config():
    cfg = EnvDiffConfig()
    assert cfg.base == ".env"
    assert cfg.targets == []
    assert cfg.format == "text"


def test_from_dict_full():
    data = {
        "base": ".env.base",
        "targets": ["prod", "staging"],
        "format": "json",
        "ignore_keys": ["DEBUG"],
        "rules": ["no_localhost"],
        "export_path": "out/report.json",
    }
    cfg = EnvDiffConfig.from_dict(data)
    assert cfg.base == ".env.base"
    assert cfg.targets == ["prod", "staging"]
    assert cfg.export_path == "out/report.json"


def test_from_dict_partial():
    cfg = EnvDiffConfig.from_dict({"base": ".env.local"})
    assert cfg.base == ".env.local"
    assert cfg.format == "text"


def test_to_dict_roundtrip():
    cfg = EnvDiffConfig(base=".env", targets=["prod"], format="table")
    d = cfg.to_dict()
    cfg2 = EnvDiffConfig.from_dict(d)
    assert cfg.base == cfg2.base
    assert cfg.targets == cfg2.targets


def test_find_config_file(config_dir):
    cfg_path = config_dir / "envdiff.json"
    write_config(cfg_path, {})
    found = find_config_file(str(config_dir))
    assert found is not None
    assert found.endswith("envdiff.json")


def test_find_config_file_missing(config_dir):
    assert find_config_file(str(config_dir)) is None


def test_load_config_from_file(config_dir):
    cfg_path = config_dir / "envdiff.json"
    write_config(cfg_path, {"base": ".env.test", "targets": ["prod"]})
    cfg = load_config(str(cfg_path))
    assert cfg.base == ".env.test"
    assert "prod" in cfg.targets


def test_load_config_auto_discover(config_dir):
    cfg_path = config_dir / "envdiff.json"
    write_config(cfg_path, {"format": "json"})
    cfg = load_config(search_dir=str(config_dir))
    assert cfg.format == "json"


def test_load_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config(path="/nonexistent/envdiff.json")


def test_load_config_no_file_returns_defaults(config_dir):
    cfg = load_config(search_dir=str(config_dir))
    assert cfg.base == ".env"
