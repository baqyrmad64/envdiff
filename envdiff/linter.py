"""High-level linter combining validator + rule engine for a full env audit."""
from dataclasses import dataclass, field
from typing import Optional

from envdiff.validator import EnvValidator, ValidationResult
from envdiff.rules import RuleEngine, RuleViolation, RuleFunc


@dataclass
class LintReport:
    environment: str
    validation: ValidationResult
    rule_violations: list[RuleViolation] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.validation.is_valid and not self.rule_violations

    @property
    def total_issues(self) -> int:
        return len(self.validation.errors) + len(self.rule_violations)

    def summary(self) -> str:
        if self.is_clean:
            return f"{self.environment}: no issues found"
        return (
            f"{self.environment}: {len(self.validation.errors)} validation issue(s), "
            f"{len(self.rule_violations)} rule violation(s)"
        )


class EnvLinter:
    """Runs validation and rule checks against one or more environments."""

    def __init__(self, extra_rules: Optional[list[RuleFunc]] = None) -> None:
        self.validator = EnvValidator()
        self.rule_engine = RuleEngine()
        if extra_rules:
            self.rule_engine.rules = self.rule_engine.rules + extra_rules

    def lint(self, env_name: str, env: dict[str, str]) -> LintReport:
        validation = self.validator.validate_env(env)
        violations = self.rule_engine.run(env_name, env)
        return LintReport(
            environment=env_name,
            validation=validation,
            rule_violations=violations,
        )

    def lint_many(self, envs: dict[str, dict[str, str]]) -> list[LintReport]:
        return [self.lint(name, env) for name, env in envs.items()]
