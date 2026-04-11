import pytest
from envdiff.differ import ValueDiff
from envdiff.differ_formatter import format_diff_table, format_diff_summary


@pytest.fixture
def empty_vs_set_diff():
    return ValueDiff(key="DB_HOST", base_value="", target_value="localhost")


@pytest.fixture
def type_mismatch_diff():
    return ValueDiff(key="PORT", base_value="8080", target_value="true")


@pytest.fixture
def localhost_diff():
    return ValueDiff(key="API_URL", base_value="https://api.example.com", target_value="http://localhost:3000")


@pytest.fixture
def mixed_diffs(empty_vs_set_diff, type_mismatch_diff, localhost_diff):
    return [empty_vs_set_diff, type_mismatch_diff, localhost_diff]


def test_table_no_diffs():
    result = format_diff_table([])
    assert "No value differences" in result


def test_table_has_header(mixed_diffs):
    result = format_diff_table(mixed_diffs, use_color=False)
    assert "KEY" in result
    assert "BASE" in result
    assert "TARGET" in result
    assert "NOTE" in result


def test_table_shows_key(mixed_diffs):
    result = format_diff_table(mixed_diffs, use_color=False)
    assert "DB_HOST" in result
    assert "PORT" in result
    assert "API_URL" in result


def test_table_shows_values(empty_vs_set_diff):
    result = format_diff_table([empty_vs_set_diff], use_color=False)
    assert "localhost" in result


def test_table_shows_note(localhost_diff):
    result = format_diff_table([localhost_diff], use_color=False)
    assert "localhost" in result.lower()


def test_summary_no_diffs():
    result = format_diff_summary([])
    assert "identical" in result.lower()


def test_summary_total_count(mixed_diffs):
    result = format_diff_summary(mixed_diffs)
    assert "Total diffs: 3" in result


def test_summary_empty_vs_set(empty_vs_set_diff):
    result = format_diff_summary([empty_vs_set_diff])
    assert "empty vs set" in result


def test_summary_type_mismatch(type_mismatch_diff):
    result = format_diff_summary([type_mismatch_diff])
    assert "type mismatch" in result


def test_summary_localhost(localhost_diff):
    result = format_diff_summary([localhost_diff])
    assert "localhost issue" in result


def test_table_color_codes_applied(mixed_diffs):
    result_color = format_diff_table(mixed_diffs, use_color=True)
    result_plain = format_diff_table(mixed_diffs, use_color=False)
    assert len(result_color) > len(result_plain)
