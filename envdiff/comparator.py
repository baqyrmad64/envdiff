"""Module for comparing parsed environment files."""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class ComparisonResult:
    """Result of comparing two environment files."""
    missing_keys: Set[str]
    extra_keys: Set[str]
    mismatched_values: Dict[str, Tuple[str, str]]
    matching_keys: Set[str]

    @property
    def has_differences(self) -> bool:
        """Check if there are any differences between the files."""
        return bool(self.missing_keys or self.extra_keys or self.mismatched_values)

    def get_summary(self) -> str:
        """Get a human-readable summary of the comparison."""
        lines = []
        if self.missing_keys:
            lines.append(f"Missing keys: {len(self.missing_keys)}")
        if self.extra_keys:
            lines.append(f"Extra keys: {len(self.extra_keys)}")
        if self.mismatched_values:
            lines.append(f"Mismatched values: {len(self.mismatched_values)}")
        if self.matching_keys:
            lines.append(f"Matching keys: {len(self.matching_keys)}")
        return ", ".join(lines) if lines else "No differences found"


class EnvComparator:
    """Compare environment variable dictionaries."""

    def __init__(self, base_env: Dict[str, str]):
        """Initialize comparator with a base environment.
        
        Args:
            base_env: The base/reference environment to compare against
        """
        self.base_env = base_env

    def compare(self, target_env: Dict[str, str]) -> ComparisonResult:
        """Compare target environment against the base.
        
        Args:
            target_env: The environment to compare against base
            
        Returns:
            ComparisonResult containing all differences
        """
        base_keys = set(self.base_env.keys())
        target_keys = set(target_env.keys())

        missing_keys = base_keys - target_keys
        extra_keys = target_keys - base_keys
        common_keys = base_keys & target_keys

        mismatched_values = {}
        matching_keys = set()

        for key in common_keys:
            if self.base_env[key] != target_env[key]:
                mismatched_values[key] = (self.base_env[key], target_env[key])
            else:
                matching_keys.add(key)

        return ComparisonResult(
            missing_keys=missing_keys,
            extra_keys=extra_keys,
            mismatched_values=mismatched_values,
            matching_keys=matching_keys
        )

    def compare_multiple(self, environments: Dict[str, Dict[str, str]]) -> Dict[str, ComparisonResult]:
        """Compare multiple environments against the base.
        
        Args:
            environments: Dictionary mapping environment names to their variables
            
        Returns:
            Dictionary mapping environment names to their comparison results
        """
        results = {}
        for env_name, env_vars in environments.items():
            results[env_name] = self.compare(env_vars)
        return results
