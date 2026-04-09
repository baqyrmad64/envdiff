"""Tests for the environment comparator module."""

import pytest
from envdiff.comparator import EnvComparator, ComparisonResult


@pytest.fixture
def base_env():
    """Sample base environment."""
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "secret123",
        "DEBUG": "true",
        "PORT": "3000"
    }


@pytest.fixture
def comparator(base_env):
    """Create a comparator with base environment."""
    return EnvComparator(base_env)


def test_compare_identical_environments(comparator, base_env):
    """Test comparing identical environments shows no differences."""
    result = comparator.compare(base_env.copy())
    
    assert not result.has_differences
    assert len(result.missing_keys) == 0
    assert len(result.extra_keys) == 0
    assert len(result.mismatched_values) == 0
    assert len(result.matching_keys) == 4


def test_compare_missing_keys(comparator):
    """Test detection of missing keys in target environment."""
    target_env = {
        "DATABASE_URL": "postgres://localhost/db",
        "API_KEY": "secret123"
    }
    
    result = comparator.compare(target_env)
    
    assert result.has_differences
    assert result.missing_keys == {"DEBUG", "PORT"}
    assert len(result.extra_keys) == 0
    assert len(result.matching_keys) == 2


def test_compare_extra_keys(comparator, base_env):
    """Test detection of extra keys in target environment."""
    target_env = base_env.copy()
    target_env["EXTRA_VAR"] = "value"
    target_env["ANOTHER_VAR"] = "another"
    
    result = comparator.compare(target_env)
    
    assert result.has_differences
    assert result.extra_keys == {"EXTRA_VAR", "ANOTHER_VAR"}
    assert len(result.missing_keys) == 0
    assert len(result.matching_keys) == 4


def test_compare_mismatched_values(comparator, base_env):
    """Test detection of mismatched values."""
    target_env = base_env.copy()
    target_env["DEBUG"] = "false"
    target_env["PORT"] = "8080"
    
    result = comparator.compare(target_env)
    
    assert result.has_differences
    assert len(result.mismatched_values) == 2
    assert result.mismatched_values["DEBUG"] == ("true", "false")
    assert result.mismatched_values["PORT"] == ("3000", "8080")
    assert len(result.matching_keys) == 2


def test_compare_multiple_environments(comparator, base_env):
    """Test comparing multiple environments at once."""
    environments = {
        "staging": {"DATABASE_URL": "postgres://staging/db", "API_KEY": "secret123", "DEBUG": "true", "PORT": "3000"},
        "production": {"DATABASE_URL": "postgres://prod/db", "API_KEY": "prod_key", "PORT": "80"}
    }
    
    results = comparator.compare_multiple(environments)
    
    assert len(results) == 2
    assert "staging" in results
    assert "production" in results
    assert results["staging"].mismatched_values["DATABASE_URL"][1] == "postgres://staging/db"
    assert "DEBUG" in results["production"].missing_keys


def test_comparison_result_summary(comparator):
    """Test the summary generation for comparison results."""
    target_env = {
        "DATABASE_URL": "postgres://other/db",
        "EXTRA_KEY": "value"
    }
    
    result = comparator.compare(target_env)
    summary = result.get_summary()
    
    assert "Missing keys: 3" in summary
    assert "Extra keys: 1" in summary
    assert "Mismatched values: 1" in summary
