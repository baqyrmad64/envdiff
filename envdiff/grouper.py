"""Groups env keys by shared prefix for structural analysis."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyGroup:
    prefix: str
    keys: List[str] = field(default_factory=list)

    def size(self) -> int:
        return len(self.keys)

    def contains(self, key: str) -> bool:
        return key in self.keys


@dataclass
class GroupResult:
    groups: Dict[str, KeyGroup] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def all_prefixes(self) -> List[str]:
        return sorted(self.groups.keys())

    def group_for(self, key: str) -> Optional[KeyGroup]:
        for group in self.groups.values():
            if group.contains(key):
                return group
        return None

    def total_grouped(self) -> int:
        return sum(g.size() for g in self.groups.values())


class EnvGrouper:
    def __init__(self, min_group_size: int = 2):
        self.min_group_size = min_group_size

    def group(self, env: Dict[str, str]) -> GroupResult:
        prefix_map: Dict[str, List[str]] = {}

        for key in env:
            parts = key.split("_")
            if len(parts) >= 2:
                prefix = parts[0]
                prefix_map.setdefault(prefix, []).append(key)
            else:
                prefix_map.setdefault("", []).append(key)

        result = GroupResult()
        for prefix, keys in prefix_map.items():
            if prefix and len(keys) >= self.min_group_size:
                result.groups[prefix] = KeyGroup(prefix=prefix, keys=sorted(keys))
            else:
                result.ungrouped.extend(keys)

        result.ungrouped = sorted(result.ungrouped)
        return result
