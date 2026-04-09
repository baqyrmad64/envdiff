"""Tests for the EnvParser module."""

import pytest
from pathlib import Path
import tempfile
import os
from envdiff.parser import EnvParser


class TestEnvParser:
    """Test suite for EnvParser class."""

    @pytest.fixture
    def parser(self):
        """Create an EnvParser instance."""
        return EnvParser()

    @pytest.fixture
    def temp_env_file(self):
        """Create a temporary .env file for testing."""
        fd, path = tempfile.mkstemp(suffix='.env')
        yield path
        os.close(fd)
        os.unlink(path)

    def test_parse_simple_key_value(self, parser, temp_env_file):
        """Test parsing simple KEY=value pairs."""
        with open(temp_env_file, 'w') as f:
            f.write('DATABASE_URL=postgres://localhost\n')
            f.write('API_KEY=secret123\n')
        
        result = parser.parse_file(temp_env_file)
        assert result == {
            'DATABASE_URL': 'postgres://localhost',
            'API_KEY': 'secret123'
        }

    def test_parse_quoted_values(self, parser, temp_env_file):
        """Test parsing values with quotes."""
        with open(temp_env_file, 'w') as f:
            f.write('SINGLE_QUOTED=\'value with spaces\'\n')
            f.write('DOUBLE_QUOTED="another value"\n')
        
        result = parser.parse_file(temp_env_file)
        assert result == {
            'SINGLE_QUOTED': 'value with spaces',
            'DOUBLE_QUOTED': 'another value'
        }

    def test_parse_with_comments(self, parser, temp_env_file):
        """Test that comments are ignored."""
        with open(temp_env_file, 'w') as f:
            f.write('# This is a comment\n')
            f.write('KEY1=value1\n')
            f.write('  # Another comment\n')
            f.write('KEY2=value2 # inline comment\n')
        
        result = parser.parse_file(temp_env_file)
        assert result == {
            'KEY1': 'value1',
            'KEY2': 'value2'
        }

    def test_parse_empty_lines(self, parser, temp_env_file):
        """Test that empty lines are ignored."""
        with open(temp_env_file, 'w') as f:
            f.write('KEY1=value1\n')
            f.write('\n')
            f.write('  \n')
            f.write('KEY2=value2\n')
        
        result = parser.parse_file(temp_env_file)
        assert result == {'KEY1': 'value1', 'KEY2': 'value2'}

    def test_parse_file_not_found(self, parser):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file('/nonexistent/file.env')

    def test_parse_multiple_files(self, parser, temp_env_file):
        """Test parsing multiple files at once."""
        # Create second temp file
        fd2, path2 = tempfile.mkstemp(suffix='.env')
        
        try:
            with open(temp_env_file, 'w') as f:
                f.write('KEY1=value1\n')
            
            with open(path2, 'w') as f:
                f.write('KEY2=value2\n')
            
            result = parser.parse_multiple([temp_env_file, path2])
            assert result[temp_env_file] == {'KEY1': 'value1'}
            assert result[path2] == {'KEY2': 'value2'}
        finally:
            os.close(fd2)
            os.unlink(path2)
