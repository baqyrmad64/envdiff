"""Built-in and custom diff rules applied during comparison."""
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class RuleViolation:
    rule_name: str
    key: str
    message: str
    environment: Optional[str] = None

    def __str__(self) -> str:
        env_tag = f" [{self.environment}]" if self.environment else ""
        return f"{self.rule_name}{env_tag} — {self.key}: {self.message}"


RuleFunc = Callable[[str, str, str], Optional[RuleViolation]]


def rule_no_localhost(env_name: str, key: str, value: str) -> Optional[RuleViolation]:
    """Warn if a production-like env contains localhost URLs."""
    if "prod" in env_name.lower() and "localhost" in value.lower():
        return RuleViolation(
            rule_name="no_localhost",
            key=key,
            message="Value contains 'localhost' in a production environment",
            environment=env_name,
        )
    return None


def rule_no_placeholder(env_name: str, key: str, value: str) -> Optional[RuleViolation]:
    """Warn if any value looks like an unfilled placeholder."""
    placeholders = {"<your_value>", "CHANGEME", "TODO", "PLACEHOLDER", "xxx"}
    if value.strip().upper() in {p.upper() for p in placeholders}:
        return RuleViolation(
            rule_name="no_placeholder",
            key=key,
            message=f"Value looks like an unfilled placeholder: '{value}'",
            environment=env_name,
        )
    return None


DEFAULT_RULES: list[RuleFunc] = [
    rule_no_localhost,
    rule_no_placeholder,
]


class RuleEngine:
    def __init__(self, rules: Optional[list[RuleFunc]] = None) -> None:
        self.rules: list[RuleFunc] = rules if rules is not None else DEFAULT_RULES

    def run(self, env_name: str, env: dict[str, str]) -> list[RuleViolation]:
        violations: list[RuleViolation] = []
        for key, value in env.items():
            for rule in self.rules:
                if violation := rule(env_name, key, value):
                    violations.append(violation)
        return violations
