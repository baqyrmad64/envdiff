"""Tests for envdiff.rules module."""
import pytest
from envdiff.rules import (
    RuleEngine,
    RuleViolation,
    rule_no_localhost,
    rule_no_placeholder,
    DEFAULT_RULES,
)


class TestRuleNoLocalhost:
    def test_triggers_on_prod_with_localhost(self):
        v = rule_no_localhost("production", "DB_URL", "http://localhost:5432")
        assert v is not None
        assert v.rule_name == "no_localhost"
        assert v.environment == "production"

    def test_no_trigger_on_dev(self):
        v = rule_no_localhost("development", "DB_URL", "http://localhost:5432")
        assert v is None

    def test_no_trigger_on_prod_without_localhost(self):
        v = rule_no_localhost("production", "DB_URL", "http://db.example.com:5432")
        assert v is None


class TestRuleNoPlaceholder:
    def test_triggers_on_changeme(self):
        v = rule_no_placeholder("staging", "SECRET", "CHANGEME")
        assert v is not None
        assert v.rule_name == "no_placeholder"

    def test_triggers_case_insensitive(self):
        v = rule_no_placeholder("staging", "SECRET", "changeme")
        assert v is not None

    def test_no_trigger_on_real_value(self):
        v = rule_no_placeholder("staging", "SECRET", "s3cr3t_v@lue")
        assert v is None

    def test_triggers_on_placeholder_tag(self):
        v = rule_no_placeholder("prod", "API_KEY", "<your_value>")
        assert v is not None


class TestRuleEngine:
    def test_engine_with_default_rules(self):
        engine = RuleEngine()
        assert engine.rules == DEFAULT_RULES

    def test_engine_finds_violation(self):
        engine = RuleEngine()
        env = {"DB_URL": "http://localhost:5432", "KEY": "real_value"}
        violations = engine.run("production", env)
        assert any(v.key == "DB_URL" for v in violations)

    def test_engine_no_violations_clean_env(self):
        engine = RuleEngine()
        env = {"DB_URL": "postgres://db.prod.example.com/app", "DEBUG": "false"}
        violations = engine.run("production", env)
        assert violations == []

    def test_engine_custom_rules_only(self):
        engine = RuleEngine(rules=[rule_no_placeholder])
        env = {"DB_URL": "http://localhost"}
        violations = engine.run("production", env)
        # no_localhost rule not loaded, so no violation
        assert violations == []

    def test_violation_str(self):
        v = RuleViolation(rule_name="my_rule", key="FOO", message="bad", environment="prod")
        assert "my_rule" in str(v)
        assert "FOO" in str(v)
        assert "prod" in str(v)
