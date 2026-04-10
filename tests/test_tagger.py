"""Tests for envdiff.tagger."""
import pytest
from envdiff.tagger import EnvTagger, TaggedKey, TagResult


@pytest.fixture
def tagger():
    return EnvTagger()


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "abc123",
        "APP_PORT": "8080",
        "ENABLE_FEATURE_X": "true",
        "DEBUG": "false",
        "AWS_ACCESS_KEY": "AKIA...",
        "APP_NAME": "myapp",
        "SMTP_HOST": "mail.example.com",
    }


def test_tag_key_secret(tagger):
    result = tagger.tag_key("API_KEY")
    assert "secret" in result.tags


def test_tag_key_database(tagger):
    result = tagger.tag_key("DATABASE_URL")
    assert "database" in result.tags


def test_tag_key_port(tagger):
    result = tagger.tag_key("APP_PORT")
    assert "port" in result.tags


def test_tag_key_feature_flag(tagger):
    result = tagger.tag_key("ENABLE_FEATURE_X")
    assert "feature_flag" in result.tags


def test_tag_key_debug(tagger):
    result = tagger.tag_key("DEBUG")
    assert "debug" in result.tags


def test_tag_key_aws(tagger):
    result = tagger.tag_key("AWS_ACCESS_KEY")
    assert "aws" in result.tags


def test_tag_key_untagged(tagger):
    result = tagger.tag_key("APP_NAME")
    assert result.tags == []
    assert result.primary_tag is None


def test_tag_key_email(tagger):
    result = tagger.tag_key("SMTP_HOST")
    assert "email" in result.tags


def test_tag_env_returns_all_keys(tagger, sample_env):
    result = tagger.tag_env(sample_env)
    assert len(result.tagged) == len(sample_env)


def test_tag_env_keys_for_tag(tagger, sample_env):
    result = tagger.tag_env(sample_env)
    secrets = result.keys_for_tag("secret")
    assert "API_KEY" in secrets


def test_tag_env_untagged_keys(tagger, sample_env):
    result = tagger.tag_env(sample_env)
    untagged = result.untagged_keys()
    assert "APP_NAME" in untagged


def test_tag_env_all_tags(tagger, sample_env):
    result = tagger.tag_env(sample_env)
    tags = result.all_tags()
    assert "secret" in tags
    assert "database" in tags


def test_extra_patterns(sample_env):
    tagger = EnvTagger(extra_patterns={"region": r"region"})
    result = tagger.tag_key("AWS_REGION")
    assert "region" in result.tags


def test_has_tag_method(tagger):
    tagged = tagger.tag_key("DB_PASSWORD")
    assert tagged.has_tag("secret")
    assert not tagged.has_tag("aws")
