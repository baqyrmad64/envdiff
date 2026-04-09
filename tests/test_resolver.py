"""Tests for envdiff.resolver."""

import os
import pytest

from envdiff.resolver import EnvResolver, ResolvedPath, ResolverResult


@pytest.fixture
def env_dir(tmp_path):
    (tmp_path / ".env.production").write_text("APP=prod\n")
    (tmp_path / ".env.staging").write_text("APP=staging\n")
    (tmp_path / "development.env").write_text("APP=dev\n")
    return str(tmp_path)


@pytest.fixture
def resolver(env_dir):
    return EnvResolver(base_dir=env_dir)


def test_resolve_dot_env_prefix(resolver, env_dir):
    result = resolver.resolve("production")
    assert result is not None
    assert result.endswith(".env.production")


def test_resolve_env_suffix(resolver, env_dir):
    result = resolver.resolve("development")
    assert result is not None
    assert "development.env" in result


def test_resolve_direct_path(resolver, env_dir):
    direct = os.path.join(env_dir, ".env.staging")
    result = resolver.resolve(direct)
    assert result == direct


def test_resolve_missing_returns_none(resolver):
    result = resolver.resolve("nonexistent")
    assert result is None


def test_resolve_many_all_found(resolver):
    result = resolver.resolve_many(["production", "staging"])
    assert result.all_found
    assert len(result.resolved) == 2
    assert len(result.unresolved) == 0


def test_resolve_many_partial(resolver):
    result = resolver.resolve_many(["production", "ghost"])
    assert not result.all_found
    assert len(result.unresolved) == 1
    assert result.unresolved[0] == "ghost"


def test_resolved_path_str():
    rp = ResolvedPath(alias="prod", path=".env.production", exists=True)
    assert "prod" in str(rp)
    assert "ok" in str(rp)


def test_resolved_path_missing_str():
    rp = ResolvedPath(alias="prod", path=".env.production", exists=False)
    assert "missing" in str(rp)


def test_resolver_result_all_found_with_missing_file(env_dir):
    result = ResolverResult(
        resolved=[ResolvedPath("x", "/fake/path", exists=False)],
        unresolved=[],
    )
    assert not result.all_found
