"""Tests for envdiff.validator module."""
import pytest
from envdiff.validator import EnvValidator, ValidationError, ValidationResult


@pytest.fixture
def validator():
    return EnvValidator()


class TestValidateKey:
    def test_valid_key(self, validator):
        assert validator.validate_key("DATABASE_URL") is None

    def test_valid_key_with_numbers(self, validator):
        assert validator.validate_key("S3_BUCKET_V2") is None

    def test_empty_key_is_error(self, validator):
        err = validator.validate_key("")
        assert err is not None
        assert err.severity == "error"

    def test_lowercase_key_is_warning(self, validator):
        err = validator.validate_key("database_url")
        assert err is not None
        assert err.severity == "warning"

    def test_key_starting_with_number_is_warning(self, validator):
        err = validator.validate_key("1_BAD_KEY")
        assert err is not None
        assert err.severity == "warning"


class TestValidateValue:
    def test_non_empty_value(self, validator):
        assert validator.validate_value("KEY", "some_value") is None

    def test_empty_value_is_warning(self, validator):
        err = validator.validate_value("KEY", "")
        assert err is not None
        assert err.severity == "warning"
        assert "empty" in err.message.lower()


class TestValidateEnv:
    def test_clean_env(self, validator):
        env = {"DATABASE_URL": "postgres://localhost", "DEBUG": "false"}
        result = validator.validate_env(env)
        assert result.is_valid
        assert not result.has_warnings
        assert result.errors == []

    def test_env_with_empty_value(self, validator):
        env = {"SECRET_KEY": ""}
        result = validator.validate_env(env)
        assert result.has_warnings

    def test_env_with_bad_key(self, validator):
        env = {"bad-key": "value"}
        result = validator.validate_env(env)
        assert result.has_warnings

    def test_validation_result_str(self, validator):
        err = ValidationError(key="MY_KEY", message="something wrong", severity="warning")
        assert "WARNING" in str(err)
        assert "MY_KEY" in str(err)
