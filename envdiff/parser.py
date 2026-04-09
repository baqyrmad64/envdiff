"""Parser module for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


class EnvParser:
    """Parse .env files and extract key-value pairs."""

    # Regex pattern for parsing .env lines
    # Supports: KEY=value, KEY="value", KEY='value', comments, empty lines
    ENV_PATTERN = re.compile(
        r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
    )
    COMMENT_PATTERN = re.compile(r'^\s*#.*$')
    EMPTY_LINE_PATTERN = re.compile(r'^\s*$')

    @staticmethod
    def _strip_quotes(value: str) -> str:
        """Remove surrounding quotes from value if present."""
        value = value.strip()
        if len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
        return value

    @staticmethod
    def _remove_inline_comment(value: str) -> str:
        """Remove inline comments from unquoted values."""
        # Only remove comments if value is not quoted
        if not (value.strip().startswith('"') or value.strip().startswith("'")):
            comment_pos = value.find('#')
            if comment_pos != -1:
                return value[:comment_pos].strip()
        return value

    def parse_file(self, filepath: str) -> Dict[str, str]:
        """Parse a .env file and return dictionary of key-value pairs.
        
        Args:
            filepath: Path to the .env file
            
        Returns:
            Dictionary mapping environment variable names to their values
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file cannot be read
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        env_vars = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments and empty lines
                if self.COMMENT_PATTERN.match(line) or self.EMPTY_LINE_PATTERN.match(line):
                    continue
                
                # Try to match key=value pattern
                match = self.ENV_PATTERN.match(line)
                if match:
                    key = match.group('key')
                    value = match.group('value')
                    value = self._remove_inline_comment(value)
                    value = self._strip_quotes(value)
                    env_vars[key] = value
                else:
                    # Line doesn't match expected format, skip it
                    continue
        
        return env_vars

    def parse_multiple(self, filepaths: list[str]) -> Dict[str, Dict[str, str]]:
        """Parse multiple .env files.
        
        Args:
            filepaths: List of paths to .env files
            
        Returns:
            Dictionary mapping filepath to parsed env vars
        """
        results = {}
        for filepath in filepaths:
            results[filepath] = self.parse_file(filepath)
        return results
