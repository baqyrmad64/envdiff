"""Sorts and groups env keys by prefix or alphabetically."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SortedEnv:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def all_keys(self) -> List[str]:
        keys = list(self.ungrouped.keys())
        for group_keys in self.groups.values():
            keys.extend(group_keys.keys())
        return keys

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())


class EnvSorter:
    def __init__(self, group_by_prefix: bool = True, separator: str = "_"):
        self.group_by_prefix = group_by_prefix
        self.separator = separator

    def sort(self, env: Dict[str, str]) -> SortedEnv:
        if not self.group_by_prefix:
            return SortedEnv(ungrouped=dict(sorted(env.items())))

        groups: Dict[str, Dict[str, str]] = {}
        ungrouped: Dict[str, str] = {}

        for key, value in sorted(env.items()):
            prefix = self._extract_prefix(key)
            if prefix:
                groups.setdefault(prefix, {})[key] = value
            else:
                ungrouped[key] = value

        # promote single-key groups back to ungrouped
        final_groups: Dict[str, Dict[str, str]] = {}
        for prefix, members in groups.items():
            if len(members) == 1:
                ungrouped.update(members)
            else:
                final_groups[prefix] = members

        return SortedEnv(groups=final_groups, ungrouped=dict(sorted(ungrouped.items())))

    def _extract_prefix(self, key: str) -> str:
        parts = key.split(self.separator, 1)
        if len(parts) > 1 and parts[0]:
            return parts[0]
        return ""

    def diff_order(self, keys: List[str]) -> List[str]:
        """Return keys sorted alphabetically for consistent diff output."""
        return sorted(keys)
