"""Tests for EnvAnnotator and AnnotationResult."""
import pytest
from pathlib import Path
from envdiff.annotator import EnvAnnotator, AnnotationResult, AnnotatedKey


@pytest.fixture
def annotator():
    return EnvAnnotator()


@pytest.fixture
def tmp_env(tmp_path):
    content = """# Database host
DB_HOST=localhost
DB_PORT=5432
# Secret token
API_TOKEN=abc123
PLAIN_KEY=value
"""
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_annotate_returns_annotation_result(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    assert isinstance(result, AnnotationResult)


def test_annotate_source_is_path_string(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    assert result.source == str(tmp_env)


def test_annotate_finds_all_keys(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    assert set(result.keys()) == {"DB_HOST", "DB_PORT", "API_TOKEN", "PLAIN_KEY"}


def test_annotate_line_numbers(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    db_host = result.get("DB_HOST")
    assert db_host is not None
    assert db_host.line_number == 2


def test_annotate_comment_attached_to_key(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    db_host = result.get("DB_HOST")
    assert db_host.comment == "Database host"


def test_annotate_key_without_comment_is_none(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    db_port = result.get("DB_PORT")
    assert db_port is not None
    assert db_port.comment is None


def test_annotate_with_comments_filters_correctly(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    commented = result.with_comments()
    keys = [e.key for e in commented]
    assert "DB_HOST" in keys
    assert "API_TOKEN" in keys
    assert "DB_PORT" not in keys


def test_annotate_missing_file_returns_empty(annotator, tmp_path):
    result = annotator.annotate(tmp_path / "nonexistent.env")
    assert result.entries == []


def test_annotated_key_to_dict(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    entry = result.get("DB_HOST")
    d = entry.to_dict()
    assert d["key"] == "DB_HOST"
    assert d["value"] == "localhost"
    assert d["comment"] == "Database host"
    assert "line_number" in d
    assert "raw_line" in d


def test_annotated_key_has_comment_true(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    assert result.get("DB_HOST").has_comment() is True


def test_annotated_key_has_comment_false(annotator, tmp_env):
    result = annotator.annotate(tmp_env)
    assert result.get("DB_PORT").has_comment() is False
