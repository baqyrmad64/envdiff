"""Merge multiple .env dicts into a unified view, tracking key origins."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MergedKey:
    key: str
    values: Dict[str, Optional[str]] = field(default_factory=dict)  # env_name -> value
    sources: List[str] = field(default_factory=list)

    @property
    def is_consistent(self) -> bool:
        """True if all present values are identical."""
        present = [v for v in self.values.values() if v is not None]
        return len(set(present)) <= 1

    @property
    def missing_in(self) -> List[str]:
        return [env for env, val in self.values.items() if val is None]


@dataclass
class MergeResult:
    keys: Dict[str, MergedKey] = field(default_factory=dict)
    env_names: List[str] = field(default_factory=list)

    @property
    def all_keys(self) -> Set[str]:
        return set(self.keys.keys())

    @property
    def inconsistent_keys(self) -> List[MergedKey]:
        return [mk for mk in self.keys.values() if not mk.is_consistent]

    @property
    def incomplete_keys(self) -> List[MergedKey]:
        return [mk for mk in self.keys.values() if mk.missing_in]


class EnvMerger:
    """Merges multiple env dicts into a single unified MergeResult."""

    def merge(self, envs: Dict[str, Dict[str, Optional[str]]]) -> MergeResult:
        """
        Args:
            envs: mapping of environment name -> parsed env dict
        Returns:
            MergeResult with all keys tracked across environments
        """
        result = MergeResult(env_names=list(envs.keys()))
        all_keys: Set[str] = set()
        for env_dict in envs.values():
            all_keys.update(env_dict.keys())

        for key in sorted(all_keys):
            merged_key = MergedKey(key=key)
            for env_name, env_dict in envs.items():
                value = env_dict.get(key)  # None if missing
                merged_key.values[env_name] = value
                if key in env_dict:
                    merged_key.sources.append(env_name)
            result.keys[key] = merged_key

        return result
