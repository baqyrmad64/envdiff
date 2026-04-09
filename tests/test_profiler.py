"""Tests for EnvProfiler."""
import pytest
from envdiff.profiler import EnvProfiler, EnvProfile


@pytest.fixture
def profiler():
    return EnvProfiler()


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DEBUG": "true",
        "DATABASE_URL": "http://localhost:5432/db",
        "SECRET_KEY": "",
        "TIMEOUT": "30.5",
        "ENABLED": "yes",
    }


def test_profile_total_keys(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert result.total_keys == 7


def test_profile_empty_values(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert "SECRET_KEY" in result.empty_values
    assert len(result.empty_values) == 1


def test_profile_numeric_values(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert "PORT" in result.numeric_values
    assert "TIMEOUT" in result.numeric_values


def test_profile_boolean_values(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert "DEBUG" in result.boolean_values
    assert "ENABLED" in result.boolean_values


def test_profile_url_values(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert "DATABASE_URL" in result.url_values


def test_profile_empty_ratio(profiler, sample_env):
    result = profiler.profile(".env", sample_env)
    assert abs(result.empty_ratio - 1 / 7) < 0.001


def test_profile_empty_env(profiler):
    result = profiler.profile(".env", {})
    assert result.total_keys == 0
    assert result.empty_ratio == 0.0
    assert result.longest_key is None


def test_profile_longest_key(profiler):
    env = {"A": "1", "LONG_KEY_NAME": "2", "MID": "3"}
    result = profiler.profile(".env", env)
    assert result.longest_key == "LONG_KEY_NAME"


def test_profile_longest_value_key(profiler):
    env = {"SHORT": "x", "LONG_VAL": "a" * 100}
    result = profiler.profile(".env", env)
    assert result.longest_value_key == "LONG_VAL"


def test_summary_keys(profiler, sample_env):
    result = profiler.profile(".env.test", sample_env)
    summary = result.summary()
    assert summary["path"] == ".env.test"
    assert "total_keys" in summary
    assert "empty_ratio" in summary
    assert "boolean_values" in summary
