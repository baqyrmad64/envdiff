"""Profile .env files to detect patterns, stats, and anomalies."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvProfile:
    """Statistical profile of a parsed .env file."""
    path: str
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    boolean_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)
    longest_key: Optional[str] = None
    longest_value_key: Optional[str] = None

    @property
    def empty_ratio(self) -> float:
        if self.total_keys == 0:
            return 0.0
        return len(self.empty_values) / self.total_keys

    def summary(self) -> Dict[str, object]:
        return {
            "path": self.path,
            "total_keys": self.total_keys,
            "empty_values": len(self.empty_values),
            "numeric_values": len(self.numeric_values),
            "boolean_values": len(self.boolean_values),
            "url_values": len(self.url_values),
            "empty_ratio": round(self.empty_ratio, 3),
            "longest_key": self.longest_key,
            "longest_value_key": self.longest_value_key,
        }


_BOOLEAN_LIKE = {"true", "false", "yes", "no", "1", "0", "on", "off"}
_URL_PREFIXES = ("http://", "https://", "ftp://")


class EnvProfiler:
    """Builds an EnvProfile from a parsed env dict."""

    def profile(self, path: str, env: Dict[str, str]) -> EnvProfile:
        result = EnvProfile(path=path, total_keys=len(env))

        longest_key = None
        longest_value_key = None
        max_key_len = -1
        max_val_len = -1

        for key, value in env.items():
            stripped = value.strip()

            if stripped == "":
                result.empty_values.append(key)
            elif stripped.lower() in _BOOLEAN_LIKE:
                result.boolean_values.append(key)
            elif stripped.startswith(_URL_PREFIXES):
                result.url_values.append(key)
            elif self._is_numeric(stripped):
                result.numeric_values.append(key)

            if len(key) > max_key_len:
                max_key_len = len(key)
                longest_key = key

            if len(value) > max_val_len:
                max_val_len = len(value)
                longest_value_key = key

        result.longest_key = longest_key
        result.longest_value_key = longest_value_key
        return result

    @staticmethod
    def _is_numeric(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
