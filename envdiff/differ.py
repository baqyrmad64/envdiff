from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ValueDiff:
    key: str
    base_value: Optional[str]
    target_value: Optional[str]

    def is_empty_vs_set(self) -> bool:
        return (self.base_value == "" and bool(self.target_value)) or \
               (self.target_value == "" and bool(self.base_value))

    def is_type_mismatch(self) -> bool:
        if self.base_value is None or self.target_value is None:
            return False
        base_is_num = self.base_value.isdigit()
        target_is_num = self.target_value.isdigit()
        base_is_bool = self.base_value.lower() in ("true", "false")
        target_is_bool = self.target_value.lower() in ("true", "false")
        return (base_is_num != target_is_num) or (base_is_bool != target_is_bool)

    def is_url_vs_localhost(self) -> bool:
        if self.base_value is None or self.target_value is None:
            return False
        values = {self.base_value.lower(), self.target_value.lower()}
        has_url = any(v.startswith("http") and "localhost" not in v for v in values)
        has_local = any("localhost" in v or "127.0.0.1" in v for v in values)
        return has_url and has_local

    def describe(self) -> str:
        if self.is_url_vs_localhost():
            return "url vs localhost"
        if self.is_empty_vs_set():
            return "empty vs set"
        if self.is_type_mismatch():
            return "type mismatch"
        return "value changed"


def diff_values(
    base: Dict[str, str],
    target: Dict[str, str],
) -> List[ValueDiff]:
    diffs = []
    common_keys = set(base.keys()) & set(target.keys())
    for key in sorted(common_keys):
        if base[key] != target[key]:
            diffs.append(ValueDiff(key=key, base_value=base[key], target_value=target[key]))
    return diffs
