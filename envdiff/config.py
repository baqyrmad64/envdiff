"""Load and validate envdiff configuration from a TOML or JSON config file."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_DEFAULT_CONFIG_FILES = ["envdiff.toml", "envdiff.json", ".envdiff.json"]


@dataclass
class EnvDiffConfig:
    base: str = ".env"
    targets: List[str] = field(default_factory=list)
    format: str = "text"
    ignore_keys: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    export_path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "EnvDiffConfig":
        return cls(
            base=data.get("base", ".env"),
            targets=data.get("targets", []),
            format=data.get("format", "text"),
            ignore_keys=data.get("ignore_keys", []),
            rules=data.get("rules", []),
            export_path=data.get("export_path"),
        )

    def to_dict(self) -> Dict:
        return {
            "base": self.base,
            "targets": self.targets,
            "format": self.format,
            "ignore_keys": self.ignore_keys,
            "rules": self.rules,
            "export_path": self.export_path,
        }


def _load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_config_file(search_dir: str = ".") -> Optional[str]:
    for name in _DEFAULT_CONFIG_FILES:
        candidate = os.path.join(search_dir, name)
        if os.path.isfile(candidate):
            return candidate
    return None


def load_config(path: Optional[str] = None, search_dir: str = ".") -> EnvDiffConfig:
    """Load config from the given path or auto-discover it."""
    if path is None:
        path = find_config_file(search_dir)
    if path is None:
        return EnvDiffConfig()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    data = _load_json(path)
    return EnvDiffConfig.from_dict(data)
