"""Tests for envdiff.differ module."""
import pytest
from envdiff.differ import ValueDiff, diff_values, _looks_numeric, _is_localhost


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "dev-secret",
        "DEBUG": "true",
        "TIMEOUT": "30",
    }


@pytest.fixture
def prod_env():
    return {
        "DB_HOST": "db.prod.example.com",
        "DB_PORT": "5432",
        "API_KEY": "prod-secret",
        "DEBUG": "false",
        "TIMEOUT": "30",
    }


def test_diff_values_returns_only_changed(base_env, prod_env):
    diffs = diff_values(base_env, prod_env, "production")
    keys = [d.key for d in diffs]
    assert "DB_HOST" in keys
    assert "API_KEY" in keys
    assert "DEBUG" in keys
    assert "DB_PORT" not in keys
    assert "TIMEOUT" not in keys


def test_diff_values_empty_when_identical(base_env):
    diffs = diff_values(base_env, base_env.copy(), "staging")
    assert diffs == []


def test_diff_values_ignores_keys_missing_from_either():
    base = {"A": "1", "B": "2"}
    target = {"A": "1", "C": "3"}
    diffs = diff_values(base, target, "staging")
    assert diffs == []


def test_value_diff_is_url_vs_localhost():
    vd = ValueDiff("DB_HOST", "localhost", "db.prod.com", "production")
    assert vd.is_url_vs_localhost is True


def test_value_diff_not_url_vs_localhost():
    vd = ValueDiff("DB_HOST", "db.staging.com", "db.prod.com", "production")
    assert vd.is_url_vs_localhost is False


def test_value_diff_is_empty_vs_set():
    vd = ValueDiff("API_KEY", "", "some-key", "production")
    assert vd.is_empty_vs_set is True


def test_value_diff_is_type_mismatch():
    vd = ValueDiff("TIMEOUT", "thirty", "30", "production")
    assert vd.is_type_mismatch is True


def test_value_diff_no_type_mismatch_both_strings():
    vd = ValueDiff("ENV", "dev", "prod", "production")
    assert vd.is_type_mismatch is False


def test_describe_includes_key_and_values():
    vd = ValueDiff("DB_HOST", "localhost", "db.prod.com", "production")
    desc = vd.describe()
    assert "DB_HOST" in desc
    assert "localhost" in desc
    assert "db.prod.com" in desc
    assert "production" in desc


def test_describe_includes_hint_for_localhost():
    vd = ValueDiff("DB_HOST", "localhost", "db.prod.com", "production")
    assert "localhost vs real URL" in vd.describe()


def test_looks_numeric_true():
    assert _looks_numeric("42") is True
    assert _looks_numeric("3.14") is True


def test_looks_numeric_false():
    assert _looks_numeric("hello") is False
    assert _looks_numeric("") is False


def test_is_localhost_variants():
    assert _is_localhost("localhost:5432") is True
    assert _is_localhost("127.0.0.1") is True
    assert _is_localhost("db.prod.com") is False
