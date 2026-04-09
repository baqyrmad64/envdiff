"""Tests for envdiff.merger."""

import pytest
from envdiff.merger import EnvMerger, MergeResult, MergedKey


@pytest.fixture
def merger():
    return EnvMerger()


@pytest.fixture
def sample_envs():
    return {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true", "API_KEY": "dev-key"},
        "staging": {"DB_HOST": "staging.db", "DEBUG": "false", "API_KEY": "stg-key"},
        "prod": {"DB_HOST": "prod.db", "DEBUG": "false"},
    }


def test_merge_collects_all_keys(merger, sample_envs):
    result = merger.merge(sample_envs)
    assert "DB_HOST" in result.all_keys
    assert "DEBUG" in result.all_keys
    assert "API_KEY" in result.all_keys


def test_merge_env_names(merger, sample_envs):
    result = merger.merge(sample_envs)
    assert result.env_names == ["dev", "staging", "prod"]


def test_merge_missing_key_is_none(merger, sample_envs):
    result = merger.merge(sample_envs)
    api_key = result.keys["API_KEY"]
    assert api_key.values["prod"] is None


def test_merge_sources_excludes_missing(merger, sample_envs):
    result = merger.merge(sample_envs)
    api_key = result.keys["API_KEY"]
    assert "prod" not in api_key.sources
    assert "dev" in api_key.sources


def test_inconsistent_keys(merger, sample_envs):
    result = merger.merge(sample_envs)
    inconsistent = {mk.key for mk in result.inconsistent_keys}
    assert "DB_HOST" in inconsistent
    assert "API_KEY" in inconsistent


def test_consistent_key(merger):
    envs = {"dev": {"PORT": "8080"}, "prod": {"PORT": "8080"}}
    result = merger.merge(envs)
    assert result.keys["PORT"].is_consistent


def test_incomplete_keys(merger, sample_envs):
    result = merger.merge(sample_envs)
    incomplete = {mk.key for mk in result.incomplete_keys}
    assert "API_KEY" in incomplete


def test_merge_empty_envs(merger):
    result = merger.merge({})
    assert result.all_keys == set()
    assert result.env_names == []


def test_merge_single_env(merger):
    result = merger.merge({"dev": {"FOO": "bar"}})
    assert "FOO" in result.all_keys
    assert result.keys["FOO"].is_consistent
    assert result.keys["FOO"].missing_in == []
