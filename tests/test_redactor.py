"""Tests for envdiff.redactor module."""

import pytest
from envdiff.redactor import EnvRedactor, RedactorConfig, REDACTED_PLACEHOLDER


@pytest.fixture
def redactor():
    return EnvRedactor()


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "SECRET_TOKEN": "xyz789",
        "PORT": "8080",
    }


def test_is_sensitive_password(redactor):
    assert redactor.is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_api_key(redactor):
    assert redactor.is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_token(redactor):
    assert redactor.is_sensitive("SECRET_TOKEN") is True


def test_is_not_sensitive_plain_key(redactor):
    assert redactor.is_sensitive("APP_NAME") is False


def test_is_not_sensitive_port(redactor):
    assert redactor.is_sensitive("PORT") is False


def test_redact_value_sensitive(redactor):
    result = redactor.redact_value("DB_PASSWORD", "hunter2")
    assert result == REDACTED_PLACEHOLDER


def test_redact_value_non_sensitive(redactor):
    result = redactor.redact_value("APP_NAME", "myapp")
    assert result == "myapp"


def test_redact_dict_masks_sensitive_keys(redactor, sample_env):
    result = redactor.redact_dict(sample_env)
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["API_KEY"] == REDACTED_PLACEHOLDER
    assert result["SECRET_TOKEN"] == REDACTED_PLACEHOLDER


def test_redact_dict_preserves_non_sensitive(redactor, sample_env):
    result = redactor.redact_dict(sample_env)
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"
    assert result["PORT"] == "8080"


def test_sensitive_keys_returns_correct_set(redactor, sample_env):
    keys = redactor.sensitive_keys(sample_env)
    assert keys == {"DB_PASSWORD", "API_KEY", "SECRET_TOKEN"}


def test_custom_pattern_via_config():
    config = RedactorConfig()
    config.add_pattern("INTERNAL")
    redactor = EnvRedactor(config)
    assert redactor.is_sensitive("INTERNAL_URL") is True


def test_custom_placeholder():
    config = RedactorConfig(placeholder="[HIDDEN]")
    redactor = EnvRedactor(config)
    result = redactor.redact_value("DB_PASSWORD", "secret")
    assert result == "[HIDDEN]"
