"""Tests for CLI interface."""
import pytest
import tempfile
import os
from pathlib import Path

from envdiff.cli import parse_args, main


class TestParseArgs:
    """Test argument parsing."""
    
    def test_parse_minimal_args(self):
        """Test parsing with minimal required arguments."""
        args = parse_args(["base.env", "target.env"])
        assert args.base == "base.env"
        assert args.targets == ["target.env"]
        assert args.format == "text"
        assert args.verbose is False
    
    def test_parse_multiple_targets(self):
        """Test parsing with multiple target files."""
        args = parse_args(["base.env", "dev.env", "staging.env", "prod.env"])
        assert args.base == "base.env"
        assert args.targets == ["dev.env", "staging.env", "prod.env"]
    
    def test_parse_format_option(self):
        """Test parsing format option."""
        args = parse_args(["base.env", "target.env", "-f", "json"])
        assert args.format == "json"
        
        args = parse_args(["base.env", "target.env", "--format", "table"])
        assert args.format == "table"
    
    def test_parse_verbose_flag(self):
        """Test parsing verbose flag."""
        args = parse_args(["base.env", "target.env", "-v"])
        assert args.verbose is True
        
        args = parse_args(["base.env", "target.env", "--verbose"])
        assert args.verbose is True
    
    def test_parse_no_color_flag(self):
        """Test parsing no-color flag."""
        args = parse_args(["base.env", "target.env", "--no-color"])
        assert args.no_color is True


class TestMain:
    """Test main CLI function."""
    
    def test_main_missing_base_file(self, capsys):
        """Test behavior when base file doesn't exist."""
        exit_code = main(["nonexistent.env", "target.env"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err
    
    def test_main_identical_files(self, tmp_path):
        """Test comparing identical files."""
        base = tmp_path / "base.env"
        target = tmp_path / "target.env"
        
        content = "KEY1=value1\nKEY2=value2\n"
        base.write_text(content)
        target.write_text(content)
        
        exit_code = main([str(base), str(target)])
        assert exit_code == 0
    
    def test_main_different_files(self, tmp_path, capsys):
        """Test comparing different files."""
        base = tmp_path / "base.env"
        target = tmp_path / "target.env"
        
        base.write_text("KEY1=value1\nKEY2=value2\n")
        target.write_text("KEY1=value1\nKEY3=value3\n")
        
        exit_code = main([str(base), str(target)])
        assert exit_code == 1
        
        captured = capsys.readouterr()
        assert "Missing keys" in captured.out or "Extra keys" in captured.out
    
    def test_main_json_format(self, tmp_path, capsys):
        """Test JSON output format."""
        base = tmp_path / "base.env"
        target = tmp_path / "target.env"
        
        base.write_text("KEY1=value1\n")
        target.write_text("KEY2=value2\n")
        
        exit_code = main([str(base), str(target), "-f", "json"])
        assert exit_code == 1
        
        captured = capsys.readouterr()
        assert "{" in captured.out
        assert "missing_keys" in captured.out
    
    def test_main_multiple_targets(self, tmp_path):
        """Test comparing multiple target files."""
        base = tmp_path / "base.env"
        target1 = tmp_path / "target1.env"
        target2 = tmp_path / "target2.env"
        
        content = "KEY1=value1\n"
        base.write_text(content)
        target1.write_text(content)
        target2.write_text(content)
        
        exit_code = main([str(base), str(target1), str(target2)])
        assert exit_code == 0
