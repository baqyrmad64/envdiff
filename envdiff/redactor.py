"""Redactor module for masking sensitive values in env output."""

from dataclasses import dataclass, field
from typing import Dict, Set

# Common patterns that indicate sensitive keys
DEFAULT_SENSITIVE_PATTERNS: Set[str] = {
    "PASSWORD",
    "SECRET",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "AUTH",
    "CREDENTIALS",
    "PASSWD",
    "ACCESS_KEY",
    "SIGNING_KEY",
}

REDACTED_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactorConfig:
    patterns: Set[str] = field(default_factory=lambda: set(DEFAULT_SENSITIVE_PATTERNS))
    placeholder: str = REDACTED_PLACEHOLDER
    case_sensitive: bool = False

    def add_pattern(self, pattern: str) -> None:
        self.patterns.add(pattern.upper() if not self.case_sensitive else pattern)


class EnvRedactor:
    def __init__(self, config: RedactorConfig | None = None):
        self.config = config or RedactorConfig()

    def is_sensitive(self, key: str) -> bool:
        """Return True if the key matches any sensitive pattern."""
        compare_key = key.upper() if not self.config.case_sensitive else key
        return any(pattern in compare_key for pattern in self.config.patterns)

    def redact_value(self, key: str, value: str) -> str:
        """Return redacted placeholder if key is sensitive, otherwise original value."""
        if self.is_sensitive(key):
            return self.config.placeholder
        return value

    def redact_dict(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a new dict with sensitive values replaced by the placeholder."""
        return {key: self.redact_value(key, value) for key, value in env.items()}

    def sensitive_keys(self, env: Dict[str, str]) -> Set[str]:
        """Return the set of keys in env that are considered sensitive."""
        return {key for key in env if self.is_sensitive(key)}
