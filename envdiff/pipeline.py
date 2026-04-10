"""High-level pipeline that ties parsing, comparison, and reporting together."""

from typing import List, Optional
from envdiff.parser import parse_file
from envdiff.comparator import EnvComparator
from envdiff.reporter import Report, ReportBuilder


class DiffPipeline:
    """Orchestrates the full diff workflow from file paths to a Report."""

    def __init__(self, base_file: str, target_files: List[str], ignore_values: bool = False):
        self.base_file = base_file
        self.target_files = target_files
        self.ignore_values = ignore_values
        self._errors: List[str] = []

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    @property
    def has_errors(self) -> bool:
        """Return True if any errors were recorded during the last run."""
        return bool(self._errors)

    def run(self) -> Optional[Report]:
        """Execute the diff pipeline and return a Report, or None if the base file fails."""
        self._errors.clear()

        try:
            base_env = parse_file(self.base_file)
        except (OSError, ValueError) as exc:
            self._errors.append(f"Failed to parse base file '{self.base_file}': {exc}")
            return None

        builder = ReportBuilder(self.base_file)

        for target in self.target_files:
            try:
                target_env = parse_file(target)
            except (OSError, ValueError) as exc:
                self._errors.append(f"Failed to parse target file '{target}': {exc}")
                continue

            comparator = EnvComparator(base_env, target_env)
            result = comparator.compare(ignore_values=self.ignore_values)
            builder.add_result(target, result)

        return builder.build()
