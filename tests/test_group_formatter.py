import pytest
from envdiff.grouper import EnvGrouper
from envdiff.group_formatter import format_group_table, format_group_summary


@pytest.fixture
def result():
    grouper = EnvGrouper(min_group_size=2)
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
    }
    return grouper.group(env)


def test_table_has_header(result):
    output = format_group_table(result)
    assert "Key Groups" in output


def test_table_shows_group_prefix(result):
    output = format_group_table(result)
    assert "DB_*" in output
    assert "AWS_*" in output


def test_table_shows_keys_in_group(result):
    output = format_group_table(result)
    assert "DB_HOST" in output
    assert "AWS_SECRET" in output


def test_table_shows_ungrouped(result):
    output = format_group_table(result, show_ungrouped=True)
    assert "PORT" in output


def test_table_hides_ungrouped(result):
    output = format_group_table(result, show_ungrouped=False)
    assert "PORT" not in output


def test_summary_shows_totals(result):
    output = format_group_summary(result)
    assert "Group Summary" in output
    assert "2" in output  # 2 groups


def test_summary_shows_ungrouped_count(result):
    output = format_group_summary(result)
    assert "1" in output  # 1 ungrouped key (PORT)


def test_summary_shows_total_keys(result):
    output = format_group_summary(result)
    assert "5" in output  # 5 total keys
