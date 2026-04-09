"""Validation rules for environment variable keys and values."""
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class ValidationError:
    key: str
    message: str
    severity: str = "warning"  # "warning" or "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)

    @property
    def has_warnings(self) -> bool:
        return any(e.severity == "warning" for e in self.errors)

    def add(self, error: ValidationError) -> None:
        self.errors.append(error)


KEY_PATTERN = re.compile(r'^[A-Z_][A-Z0-9_]*$')


class EnvValidator:
    """Validates environment variable keys and values against common rules."""

    def validate_key(self, key: str) -> Optional[ValidationError]:
        if not key:
            return ValidationError(key="(empty)", message="Key must not be empty", severity="error")
        if not KEY_PATTERN.match(key):
            return ValidationError(
                key=key,
                message=f"Key '{key}' should match pattern [A-Z_][A-Z0-9_]* (conventional uppercase)",
                severity="warning",
            )
        return None

    def validate_value(self, key: str, value: str) -> Optional[ValidationError]:
        if value == "":
            return ValidationError(
                key=key,
                message="Value is empty — may be intentional but worth checking",
                severity="warning",
            )
        return None

    def validate_env(self, env: dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        for key, value in env.items():
            if err := self.validate_key(key):
                result.add(err)
            if err := self.validate_value(key, value):
                result.add(err)
        return result
