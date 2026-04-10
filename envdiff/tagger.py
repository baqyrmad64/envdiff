"""Tag env keys by category based on naming patterns."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

TAG_PATTERNS: Dict[str, str] = {
    "secret": r"(secret|password|passwd|token|api_key|private|credential)",
    "database": r"(db_|database|postgres|mysql|mongo|redis|sqlite)",
    "url": r"(url|host|endpoint|uri|domain|base_path)",
    "port": r"port$",
    "feature_flag": r"(enable_|disable_|feature_|flag_)",
    "debug": r"(debug|verbose|log_level|trace)",
    "aws": r"(aws_|amazon)",
    "email": r"(email|smtp|mail)",
}


@dataclass
class TaggedKey:
    key: str
    tags: List[str] = field(default_factory=list)

    @property
    def primary_tag(self) -> Optional[str]:
        return self.tags[0] if self.tags else None

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class TagResult:
    tagged: List[TaggedKey] = field(default_factory=list)

    def keys_for_tag(self, tag: str) -> List[str]:
        return [t.key for t in self.tagged if t.has_tag(tag)]

    def untagged_keys(self) -> List[str]:
        return [t.key for t in self.tagged if not t.tags]

    def all_tags(self) -> List[str]:
        seen = []
        for t in self.tagged:
            for tag in t.tags:
                if tag not in seen:
                    seen.append(tag)
        return seen


class EnvTagger:
    def __init__(self, extra_patterns: Optional[Dict[str, str]] = None):
        self._patterns = dict(TAG_PATTERNS)
        if extra_patterns:
            self._patterns.update(extra_patterns)
        self._compiled = {
            tag: re.compile(pattern, re.IGNORECASE)
            for tag, pattern in self._patterns.items()
        }

    def tag_key(self, key: str) -> TaggedKey:
        tags = [
            tag for tag, rx in self._compiled.items() if rx.search(key)
        ]
        return TaggedKey(key=key, tags=tags)

    def tag_env(self, env: Dict[str, str]) -> TagResult:
        return TagResult(tagged=[self.tag_key(k) for k in env])
