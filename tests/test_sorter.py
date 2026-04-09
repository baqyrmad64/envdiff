import pytest
from envdiff.sorter import EnvSorter, SortedEnv


@pytest.fixture
def sorter():
    return EnvSorter(group_by_prefix=True)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_sort_groups_by_prefix(sorter, sample_env):
    result = sorter.sort(sample_env)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_sort_ungrouped_singles(sorter, sample_env):
    result = sorter.sort(sample_env)
    # DEBUG and PORT have no siblings, should be ungrouped
    assert "DEBUG" in result.ungrouped
    assert "PORT" in result.ungrouped


def test_group_contains_correct_keys(sorter, sample_env):
    result = sorter.sort(sample_env)
    assert set(result.groups["DB"].keys()) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_all_keys_covers_everything(sorter, sample_env):
    result = sorter.sort(sample_env)
    assert set(result.all_keys()) == set(sample_env.keys())


def test_group_names_sorted(sorter, sample_env):
    result = sorter.sort(sample_env)
    names = result.group_names()
    assert names == sorted(names)


def test_no_grouping_mode(sample_env):
    sorter = EnvSorter(group_by_prefix=False)
    result = sorter.sort(sample_env)
    assert result.groups == {}
    assert set(result.ungrouped.keys()) == set(sample_env.keys())


def test_ungrouped_is_sorted_alphabetically(sample_env):
    sorter = EnvSorter(group_by_prefix=False)
    result = sorter.sort(sample_env)
    keys = list(result.ungrouped.keys())
    assert keys == sorted(keys)


def test_diff_order_returns_sorted_keys(sorter):
    keys = ["Z_KEY", "A_KEY", "M_KEY"]
    assert sorter.diff_order(keys) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_empty_env(sorter):
    result = sorter.sort({})
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.all_keys() == []
