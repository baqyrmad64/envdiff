"""Generate .env template files from parsed environments."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateKey:
    key: str
    placeholder: str
    comment: Optional[str] = None
    required: bool = True

    def render(self) -> str:
        lines = []
        if self.comment:
            lines.append(f"# {self.comment}")
        marker = "# REQUIRED" if self.required else "# OPTIONAL"
        lines.append(f"{self.key}={self.placeholder}  {marker}")
        return "\n".join(lines)


@dataclass
class TemplateResult:
    keys: List[TemplateKey] = field(default_factory=list)
    source_name: str = ""

    def render(self) -> str:
        header = f"# .env template generated from: {self.source_name}\n"
        body = "\n".join(k.render() for k in self.keys)
        return header + body

    @property
    def total_keys(self) -> int:
        return len(self.keys)

    @property
    def required_keys(self) -> List[TemplateKey]:
        return [k for k in self.keys if k.required]

    @property
    def optional_keys(self) -> List[TemplateKey]:
        return [k for k in self.keys if not k.required]


class EnvTemplater:
    SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth")
    OPTIONAL_PATTERNS = ("debug", "verbose", "log_level", "port", "host")

    def __init__(self, placeholder: str = "CHANGE_ME"):
        self._placeholder = placeholder

    def _is_optional(self, key: str) -> bool:
        lower = key.lower()
        return any(p in lower for p in self.OPTIONAL_PATTERNS)

    def _make_placeholder(self, key: str, value: str) -> str:
        lower = key.lower()
        if any(p in lower for p in self.SENSITIVE_PATTERNS):
            return "<secret>"
        if value and value.isdigit():
            return "<number>"
        if value and value.lower() in ("true", "false"):
            return "<bool>"
        return self._placeholder

    def generate(self, env: Dict[str, str], source_name: str = "env") -> TemplateResult:
        keys = []
        for key, value in sorted(env.items()):
            placeholder = self._make_placeholder(key, value)
            required = not self._is_optional(key)
            keys.append(TemplateKey(
                key=key,
                placeholder=placeholder,
                required=required,
            ))
        return TemplateResult(keys=keys, source_name=source_name)

    def generate_merged(self, envs: Dict[str, Dict[str, str]]) -> TemplateResult:
        """Generate a template covering all keys across multiple envs."""
        all_keys: Dict[str, str] = {}
        for env in envs.values():
            for k, v in env.items():
                all_keys.setdefault(k, v)
        return self.generate(all_keys, source_name="merged")
