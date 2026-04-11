import pytest
from envdiff.differ import ValueDiff, diff_values


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "db.example.com",
        "PORT": "5432",
        "DEBUG": "false",
        "API_URL": "https://api.example.com",
        "SECRET": "abc123",
        "EMPTY_KEY": "",
    }


@pytest.fixture
def prod_env():
    return {
        "DB_HOST": "db.example.com",
        "PORT": "true",
        "DEBUG": "false",
        "API_URL": "http://localhost:3000",
        "SECRET": "xyz789",
        "EMPTY_KEY": "now_set",
    }


def test_diff_values_returns_only_changed(base_env, prod_env):
    diffs = diff_values(base_env, prod_env)
    keys = [d.key for d in diffs]
    assert "DEBUG" not in keys
    assert "DB_HOST" not in keys


def test_diff_values_empty_when_identical():
    env = {"KEY": "value"}
    assert diff_values(env, env) == []


def test_diff_values_ignores_keys_missing_from_either(base_env):
    other = {"DB_HOST": "db.example.com", "NEW_KEY": "something"}
    diffs = diff_values(base_env, other)
    keys = [d.key for d in diffs]
    assert "NEW_KEY" not in keys


def test_is_empty_vs_set_base_empty():
    d = ValueDiff(key="X", base_value="", target_value="hello")
    assert d.is_empty_vs_set() is True


def test_is_empty_vs_set_target_empty():
    d = ValueDiff(key="X", base_value="hello", target_value="")
    assert d.is_empty_vs_set() is True


def test_is_empty_vs_set_both_set():
    d = ValueDiff(key="X", base_value="a", target_value="b")
    assert d.is_empty_vs_set() is False


def test_is_type_mismatch_num_vs_bool():
    d = ValueDiff(key="PORT", base_value="8080", target_value="true")
    assert d.is_type_mismatch() is True


def test_is_type_mismatch_same_type():
    d = ValueDiff(key="PORT", base_value="8080", target_value="9090")
    assert d.is_type_mismatch() is False


def test_is_url_vs_localhost():
    d = ValueDiff(key="API", base_value="https://api.example.com", target_value="http://localhost:3000")
    assert d.is_url_vs_localhost() is True


def test_is_url_vs_localhost_both_remote():
    d = ValueDiff(key="API", base_value="https://api.example.com", target_value="https://staging.example.com")
    assert d.is_url_vs_localhost() is False


def test_describe_url_vs_localhost():
    d = ValueDiff(key="API", base_value="https://api.example.com", target_value="http://localhost:3000")
    assert d.describe() == "url vs localhost"


def test_describe_empty_vs_set():
    d = ValueDiff(key="X", base_value="", target_value="hello")
    assert d.describe() == "empty vs set"


def test_describe_type_mismatch():
    d = ValueDiff(key="PORT", base_value="8080", target_value="true")
    assert d.describe() == "type mismatch"


def test_describe_generic_change():
    d = ValueDiff(key="SECRET", base_value="abc", target_value="xyz")
    assert d.describe() == "value changed"
