import pytest
from envdiff.grouper import EnvGrouper, KeyGroup, GroupResult


@pytest.fixture
def grouper():
    return EnvGrouper(min_group_size=2)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_group_by_prefix(grouper, sample_env):
    result = grouper.group(sample_env)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_group_contains_correct_keys(grouper, sample_env):
    result = grouper.group(sample_env)
    assert "DB_HOST" in result.groups["DB"].keys
    assert "DB_PORT" in result.groups["DB"].keys
    assert "DB_NAME" in result.groups["DB"].keys


def test_ungrouped_singles(grouper, sample_env):
    result = grouper.group(sample_env)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_min_group_size_respected():
    grouper = EnvGrouper(min_group_size=3)
    env = {"AWS_KEY": "a", "AWS_SECRET": "b", "PORT": "80"}
    result = grouper.group(env)
    # AWS only has 2 keys, below min_group_size=3
    assert "AWS" not in result.groups
    assert "AWS_KEY" in result.ungrouped
    assert "AWS_SECRET" in result.ungrouped


def test_all_prefixes_sorted(grouper, sample_env):
    result = grouper.group(sample_env)
    prefixes = result.all_prefixes()
    assert prefixes == sorted(prefixes)


def test_total_grouped(grouper, sample_env):
    result = grouper.group(sample_env)
    assert result.total_grouped() == 5  # 3 DB + 2 AWS


def test_group_for_key(grouper, sample_env):
    result = grouper.group(sample_env)
    group = result.group_for("DB_HOST")
    assert group is not None
    assert group.prefix == "DB"


def test_group_for_ungrouped_key(grouper, sample_env):
    result = grouper.group(sample_env)
    assert result.group_for("PORT") is None


def test_empty_env(grouper):
    result = grouper.group({})
    assert result.groups == {}
    assert result.ungrouped == []


def test_group_size(grouper, sample_env):
    result = grouper.group(sample_env)
    assert result.groups["DB"].size() == 3
    assert result.groups["AWS"].size() == 2
